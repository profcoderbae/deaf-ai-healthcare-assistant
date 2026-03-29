"""
Sign Language Detection Service
================================
Adapted from COS301-SE-2025/Hands-Up architecture.

Uses MediaPipe Tasks API for sign language recognition:
  1. GestureRecognizer (ML model) - Google's pre-trained model for reliable
     gesture detection: Open_Palm, Closed_Fist, Thumb_Up, Thumb_Down,
     Victory, ILoveYou, Pointing_Up
  2. HandLandmarker - 21 hand landmarks for custom geometric classification
     of additional medical gestures, ASL letters, and numbers
  3. Motion detection - Frame sequences for wave, nod, etc.

This provides both ML-based accuracy FROM a public open-source model AND
custom medical gesture support without requiring TensorFlow.
"""

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import math
import time
import os
import urllib.request
from collections import deque

# Path for the downloaded models
_MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models')
_HAND_MODEL_PATH = os.path.join(_MODEL_DIR, 'hand_landmarker.task')
_HAND_MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task'
_GESTURE_MODEL_PATH = os.path.join(_MODEL_DIR, 'gesture_recognizer.task')
_GESTURE_MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/latest/gesture_recognizer.task'


def _ensure_model(path, url, name):
    """Download a model if it doesn't exist."""
    if os.path.exists(path):
        return
    os.makedirs(_MODEL_DIR, exist_ok=True)
    print(f'[SignDetector] Downloading {name}...')
    urllib.request.urlretrieve(url, path)
    print(f'[SignDetector] {name} downloaded to {path}')


# Map ML GestureRecognizer labels → our internal gesture names
_ML_GESTURE_MAP = {
    'Open_Palm': 'open_palm',
    'Closed_Fist': 'fist',
    'Thumb_Up': 'thumbs_up',
    'Thumb_Down': 'thumbs_down',
    'Victory': 'peace',
    'ILoveYou': 'ily',
    'Pointing_Up': 'pointing',
}


class SignDetector:
    """Server-side sign language detector using MediaPipe Tasks API.

    Uses two models:
      - GestureRecognizer: Google's pre-trained ML model (open-source)
        for reliable gesture classification
      - HandLandmarker: For landmark extraction used by custom geometric
        classifiers for additional medical/ASL signs
    """

    def __init__(self):
        self.detector = None
        self.gesture_recognizer = None
        self.available = False

        try:
            # Download both models
            _ensure_model(_HAND_MODEL_PATH, _HAND_MODEL_URL, 'hand landmarker model')
            _ensure_model(_GESTURE_MODEL_PATH, _GESTURE_MODEL_URL, 'gesture recognizer model (Google ML)')

            # Init HandLandmarker (for landmarks + custom gestures)
            hand_options = mp_vision.HandLandmarkerOptions(
                base_options=mp_python.BaseOptions(model_asset_path=_HAND_MODEL_PATH),
                num_hands=1,
                min_hand_detection_confidence=0.5,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self.detector = mp_vision.HandLandmarker.create_from_options(hand_options)

            # Init GestureRecognizer (Google's pre-trained ML model)
            gesture_options = mp_vision.GestureRecognizerOptions(
                base_options=mp_python.BaseOptions(model_asset_path=_GESTURE_MODEL_PATH),
                num_hands=1,
                min_hand_detection_confidence=0.5,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self.gesture_recognizer = mp_vision.GestureRecognizer.create_from_options(gesture_options)

            self.available = True
            print('[SignDetector] ML GestureRecognizer loaded (Open_Palm, Closed_Fist, Thumb_Up, Thumb_Down, Victory, ILoveYou, Pointing_Up)')
        except Exception as e:
            print(f'[SignDetector] WARNING: Could not initialize MediaPipe: {e}')
            print('[SignDetector] Sign detection will be unavailable. Chatbot features still work.')

        # Motion buffer for word-level detection
        self.frame_buffer = deque(maxlen=30)
        self.last_prediction_time = 0
        self.cooldown = 1.5  # seconds between predictions

    def process_frame(self, image_bytes):
        """
        Process a single camera frame.
        Returns hand landmarks as normalized (x,y) pairs, or None.
        """
        if not self.available:
            return None

        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            return None

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        results = self.detector.detect(mp_image)

        if not results.hand_landmarks:
            return None

        hand = results.hand_landmarks[0]
        # Extract normalized landmark coordinates (matching Hands-Up format)
        landmarks = []
        x_list = [lm.x for lm in hand]
        y_list = [lm.y for lm in hand]
        min_x, min_y = min(x_list), min(y_list)

        for lm in hand:
            landmarks.append(lm.x - min_x)
            landmarks.append(lm.y - min_y)

        return np.array(landmarks, dtype=np.float32)

    def detect_ml_gesture(self, image_bytes):
        """
        Use Google's pre-trained GestureRecognizer ML model (open-source)
        to classify hand gestures. Much more accurate than rule-based.
        Returns (gesture_name, confidence) or (None, 0).
        """
        if not self.available:
            return None, 0.0

        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            return None, 0.0

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        try:
            result = self.gesture_recognizer.recognize(mp_image)
        except Exception:
            return None, 0.0

        if not result.gestures or not result.gestures[0]:
            return None, 0.0

        top_gesture = result.gestures[0][0]
        label = top_gesture.category_name
        score = top_gesture.score

        if label == 'None' or score < 0.50:
            return None, 0.0

        # Map ML label to our internal name
        internal = _ML_GESTURE_MAP.get(label)
        if internal:
            return internal, score

        return None, 0.0

    def detect_letter(self, landmarks):
        """
        Classify ASL fingerspelling letter from 42-feature landmark vector.
        Uses geometric rules based on finger extension and angles.
        Returns (letter, confidence) or (None, 0).
        """
        if landmarks is None or len(landmarks) != 42:
            return None, 0.0

        fingers = self._get_finger_states(landmarks)
        angles = self._get_finger_angles(landmarks)
        thumb_ext, index_ext, middle_ext, ring_ext, pinky_ext = fingers

        # Landmark positions (x,y pairs at indices 0,1 ... 40,41)
        def pt(i):
            return landmarks[i * 2], landmarks[i * 2 + 1]

        wrist = pt(0)
        thumb_tip = pt(4)
        index_tip = pt(8)
        middle_tip = pt(12)
        ring_tip = pt(16)
        pinky_tip = pt(20)
        index_mcp = pt(5)
        middle_mcp = pt(9)
        ring_mcp = pt(13)
        pinky_mcp = pt(17)
        index_pip = pt(6)
        thumb_ip = pt(3)

        # Distance helper
        def dist(a, b):
            return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

        # Check if tips are close together
        def tips_close(a, b, threshold=0.06):
            return dist(a, b) < threshold

        # Classify based on finger states and geometry
        # A: Fist, thumb to side
        if not index_ext and not middle_ext and not ring_ext and not pinky_ext and thumb_ext:
            return 'A', 0.82

        # B: All fingers up, thumb tucked
        if index_ext and middle_ext and ring_ext and pinky_ext and not thumb_ext:
            # Check fingers are together (not spread)
            if dist(index_tip, middle_tip) < 0.08 and dist(ring_tip, pinky_tip) < 0.08:
                return 'B', 0.80

        # C: Curved hand (all fingers partially bent, forming C shape)
        if thumb_ext and not index_ext and not middle_ext and not ring_ext and not pinky_ext:
            thumb_index_gap = dist(thumb_tip, index_tip)
            if 0.05 < thumb_index_gap < 0.20:
                return 'C', 0.70

        # D: Index up, others touching thumb
        if index_ext and not middle_ext and not ring_ext and not pinky_ext:
            if tips_close(middle_tip, thumb_tip, 0.08):
                return 'D', 0.80

        # E: All fingers curled, thumb tucked
        if not index_ext and not middle_ext and not ring_ext and not pinky_ext and not thumb_ext:
            return 'E', 0.72

        # F: Thumb and index touching, others extended
        if middle_ext and ring_ext and pinky_ext and tips_close(thumb_tip, index_tip, 0.06):
            return 'F', 0.78

        # G: Index pointing sideways, thumb parallel
        if index_ext and not middle_ext and not ring_ext and not pinky_ext and thumb_ext:
            # G: index points to the side (x-dominant direction)
            idx_dir_x = abs(index_tip[0] - index_mcp[0])
            idx_dir_y = abs(index_tip[1] - index_mcp[1])
            if idx_dir_x > idx_dir_y:
                return 'G', 0.72

        # H: Index and middle pointing sideways
        if index_ext and middle_ext and not ring_ext and not pinky_ext:
            idx_dir_x = abs(index_tip[0] - index_mcp[0])
            idx_dir_y = abs(index_tip[1] - index_mcp[1])
            if idx_dir_x > idx_dir_y:
                return 'H', 0.72

        # I: Pinky up only
        if not index_ext and not middle_ext and not ring_ext and pinky_ext and not thumb_ext:
            return 'I', 0.85

        # K: Index and middle up, thumb between (like peace but thumb out)
        if index_ext and middle_ext and not ring_ext and not pinky_ext and thumb_ext:
            return 'K', 0.70

        # L: Index up, thumb out (L shape)
        if index_ext and not middle_ext and not ring_ext and not pinky_ext and thumb_ext:
            idx_dir_y = index_tip[1] - index_mcp[1]
            if idx_dir_y < -0.05:  # index pointing up
                return 'L', 0.82

        # M: Thumb under three fingers (fist variation)
        # N: Thumb under two fingers
        # These are hard to distinguish geometrically — group as fist variants
        if not index_ext and not middle_ext and not ring_ext and not pinky_ext:
            if thumb_tip[1] > index_mcp[1]:  # thumb below fingers
                return 'M', 0.55

        # O: All fingertips touching thumb (O shape)
        if tips_close(index_tip, thumb_tip, 0.06) and tips_close(middle_tip, thumb_tip, 0.08):
            if not ring_ext and not pinky_ext:
                return 'O', 0.72

        # P: Like K but pointing down
        if index_ext and middle_ext and not ring_ext and not pinky_ext:
            if index_tip[1] > index_mcp[1]:  # pointing down
                return 'P', 0.68

        # Q: Like G but pointing down
        if index_ext and not middle_ext and not ring_ext and not pinky_ext and thumb_ext:
            if index_tip[1] > index_mcp[1]:
                return 'Q', 0.65

        # R: Crossed index and middle
        if index_ext and middle_ext and not ring_ext and not pinky_ext:
            if tips_close(index_tip, middle_tip, 0.04):
                return 'R', 0.70

        # S: Fist with thumb over fingers
        if not index_ext and not middle_ext and not ring_ext and not pinky_ext:
            if thumb_tip[1] < index_pip[1]:  # thumb on top
                return 'S', 0.65

        # T: Thumb between index and middle (similar to fist)
        # Hard to distinguish — falls through to E/S/A

        # U: Index and middle together, pointing up
        if index_ext and middle_ext and not ring_ext and not pinky_ext and not thumb_ext:
            if tips_close(index_tip, middle_tip, 0.06):
                return 'U', 0.75
            else:
                return 'V', 0.78  # V: spread apart

        # W: Three middle fingers up (index, middle, ring)
        if index_ext and middle_ext and ring_ext and not pinky_ext:
            return 'W', 0.76

        # X: Index hooked
        if not middle_ext and not ring_ext and not pinky_ext:
            # index partially bent
            idx_curl = dist(index_tip, index_mcp)
            if 0.05 < idx_curl < 0.15:
                return 'X', 0.60

        # Y: Thumb and pinky out
        if not index_ext and not middle_ext and not ring_ext and pinky_ext and thumb_ext:
            return 'Y', 0.85

        return None, 0.0

    def detect_number(self, landmarks):
        """
        Classify ASL numbers 0-9 from landmarks.
        Returns (number_str, confidence) or (None, 0).
        """
        if landmarks is None or len(landmarks) != 42:
            return None, 0.0

        fingers = self._get_finger_states(landmarks)
        thumb_ext, index_ext, middle_ext, ring_ext, pinky_ext = fingers
        count = sum([index_ext, middle_ext, ring_ext, pinky_ext])

        def pt(i):
            return landmarks[i * 2], landmarks[i * 2 + 1]

        thumb_tip = pt(4)
        index_tip = pt(8)

        def dist(a, b):
            return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

        # 0: O shape (thumb and index touching)
        if dist(thumb_tip, index_tip) < 0.06 and not middle_ext and not ring_ext and not pinky_ext:
            return '0', 0.75

        # 1: Index only
        if index_ext and count == 1 and not thumb_ext:
            return '1', 0.85

        # 2: Index + middle (V shape)
        if index_ext and middle_ext and count == 2 and not thumb_ext:
            return '2', 0.82

        # 3: Thumb + index + middle
        if thumb_ext and index_ext and middle_ext and count == 2:
            return '3', 0.78

        # 4: All fingers up, no thumb
        if count == 4 and not thumb_ext:
            return '4', 0.80

        # 5: All fingers + thumb
        if count == 4 and thumb_ext:
            return '5', 0.85

        # 6: Thumb + pinky
        if thumb_ext and pinky_ext and count == 1:
            return '6', 0.78

        # 7: Thumb + index + middle + ring (pinky down)
        if thumb_ext and index_ext and middle_ext and ring_ext and not pinky_ext:
            return '7', 0.72

        # 8: Thumb + index + middle (middle extended differently)
        if thumb_ext and count == 3 and not pinky_ext:
            return '8', 0.65

        # 9: Thumb + index touching with curl (like F shape)
        if dist(thumb_tip, index_tip) < 0.06 and middle_ext and ring_ext and pinky_ext:
            return '9', 0.72

        return None, 0.0

    def detect_gesture(self, landmarks):
        """
        Detect gesture/word signs from hand landmarks.
        Checks SPECIFIC (rare) gestures first, then COMMON ones last
        to avoid false positives eating up more specific signs.
        Returns (gesture_name, confidence) or (None, 0).
        """
        if landmarks is None or len(landmarks) != 42:
            return None, 0.0

        fingers = self._get_finger_states(landmarks)
        thumb_ext, index_ext, middle_ext, ring_ext, pinky_ext = fingers
        extended_count = sum([thumb_ext, index_ext, middle_ext, ring_ext, pinky_ext])

        def pt(i):
            return landmarks[i * 2], landmarks[i * 2 + 1]

        wrist = pt(0)
        thumb_tip = pt(4)
        index_tip = pt(8)
        middle_tip = pt(12)
        ring_tip = pt(16)
        pinky_tip = pt(20)
        index_mcp = pt(5)
        middle_mcp = pt(9)
        pinky_mcp = pt(17)

        def dist(a, b):
            return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

        # Palm size reference for adaptive thresholds
        palm_size = dist(wrist, middle_mcp)
        if palm_size < 0.01:
            palm_size = 0.15  # fallback

        # ─── 1. PINCH (thumb + index tips touching, others relaxed) → Pain ───
        thumb_index_dist = dist(thumb_tip, index_tip)
        if thumb_index_dist < (palm_size * 0.45) and not middle_ext and not ring_ext:
            # Additional check: thumb and index are close but rest are down
            if not pinky_ext:
                return 'pinch', 0.88

        # ─── 2. OK SIGN (thumb + index circle, other 3 fingers extended) ───
        if thumb_index_dist < (palm_size * 0.45) and middle_ext and ring_ext and pinky_ext:
            return 'ok_sign', 0.88

        # ─── 3. HORNS (index + pinky up, middle + ring down, no thumb) ───
        if index_ext and pinky_ext and not middle_ext and not ring_ext and not thumb_ext:
            return 'horns', 0.85

        # ─── 4. CALL ME (thumb + pinky extended, others curled) ───
        if thumb_ext and pinky_ext and not index_ext and not middle_ext and not ring_ext:
            return 'call_me', 0.85

        # ─── 5. ILY — I Love You (thumb + index + pinky, no middle/ring) ───
        if thumb_ext and index_ext and pinky_ext and not middle_ext and not ring_ext:
            return 'ily', 0.88

        # ─── 6. THREE UP (index + middle + ring, no thumb, no pinky) → Medicine ───
        if index_ext and middle_ext and ring_ext and not pinky_ext and not thumb_ext:
            return 'three_up', 0.85

        # ─── 7. FOUR UP (all fingers except thumb) → Wait ───
        if not thumb_ext and index_ext and middle_ext and ring_ext and pinky_ext:
            return 'four_up', 0.82

        # ─── 8. L-SHAPE (thumb + index only) → Need ───
        if thumb_ext and index_ext and not middle_ext and not ring_ext and not pinky_ext:
            return 'thumb_index_l', 0.85

        # ─── 9. PEACE / V (index + middle, no others, no thumb) ───
        if index_ext and middle_ext and not ring_ext and not pinky_ext and not thumb_ext:
            finger_spread = dist(index_tip, middle_tip)
            if finger_spread > (palm_size * 0.25):
                return 'peace', 0.85

        # ─── 10. POINTING (index only, no thumb) ───
        if index_ext and not thumb_ext and not middle_ext and not ring_ext and not pinky_ext:
            return 'pointing', 0.85

        # ─── 11. THUMBS UP / DOWN (only thumb extended) ───
        if thumb_ext and not index_ext and not middle_ext and not ring_ext and not pinky_ext:
            # Check thumb direction relative to hand center
            palm_y = (wrist[1] + index_mcp[1] + pinky_mcp[1]) / 3
            if thumb_tip[1] < (palm_y - palm_size * 0.15):
                return 'thumbs_up', 0.90
            elif thumb_tip[1] > (palm_y + palm_size * 0.15):
                return 'thumbs_down', 0.88
            else:
                # Ambiguous direction — default to thumbs_up
                return 'thumbs_up', 0.70

        # ─── 12. FIST (nothing extended) ───
        if extended_count == 0:
            return 'fist', 0.88

        # ─── 13. OPEN PALM vs FLAT DOWN (all 5 extended) ───
        if thumb_ext and index_ext and middle_ext and ring_ext and pinky_ext:
            # Check finger direction: are fingertips below wrist (palm down)?
            avg_tip_y = (index_tip[1] + middle_tip[1] + ring_tip[1] + pinky_tip[1]) / 4
            avg_mcp_y = (index_mcp[1] + middle_mcp[1] + pt(13)[1] + pinky_mcp[1]) / 4
            finger_direction = avg_tip_y - avg_mcp_y
            # Positive = tips below MCPs = pointing down = flat/palm down
            if finger_direction > (palm_size * 0.15):
                return 'flat_down', 0.85
            return 'open_palm', 0.90

        return None, 0.0

    def detect_word_from_motion(self, frame_landmarks_list):
        """
        Detect ASL word-level signs from a sequence of landmark frames.
        Uses motion patterns similar to Hands-Up wordsControllerS approach.
        Returns (word, confidence) or (None, 0).
        """
        if len(frame_landmarks_list) < 8:
            return None, 0.0

        # Calculate motion metrics
        motions = []
        for i in range(1, len(frame_landmarks_list)):
            prev = frame_landmarks_list[i - 1]
            curr = frame_landmarks_list[i]
            if prev is not None and curr is not None:
                diff = np.linalg.norm(curr - prev)
                motions.append(diff)

        if not motions:
            return None, 0.0

        avg_motion = np.mean(motions)
        max_motion = np.max(motions)

        # Get finger states from last frame
        last_lm = frame_landmarks_list[-1]
        if last_lm is None:
            return None, 0.0

        fingers = self._get_finger_states(last_lm)
        first_lm = frame_landmarks_list[0]
        if first_lm is None:
            return None, 0.0

        def pt(lm, i):
            return lm[i * 2], lm[i * 2 + 1]

        # Wave detection (Hello/Goodbye)
        wrist_positions = []
        for lm in frame_landmarks_list:
            if lm is not None:
                wrist_positions.append(pt(lm, 0))

        if len(wrist_positions) >= 5:
            x_changes = [wrist_positions[i+1][0] - wrist_positions[i][0]
                         for i in range(len(wrist_positions) - 1)]
            direction_changes = sum(1 for i in range(len(x_changes) - 1)
                                    if x_changes[i] * x_changes[i+1] < 0)
            if direction_changes >= 3 and all(fingers):
                return 'Hello', 0.85

        # Nod detection (Yes) — vertical motion of fist
        if not any(fingers[1:]) and fingers[0]:  # Thumbs up fist-ish
            y_tip = [pt(lm, 0)[1] for lm in frame_landmarks_list if lm is not None]
            if len(y_tip) >= 5:
                y_changes = [y_tip[i+1] - y_tip[i] for i in range(len(y_tip) - 1)]
                vert_changes = sum(1 for i in range(len(y_changes) - 1)
                                   if y_changes[i] * y_changes[i+1] < 0)
                if vert_changes >= 2:
                    return 'Yes', 0.78

        # Side-to-side (No) — horizontal motion of pointed finger
        if fingers[1] and not any(fingers[2:]):  # pointing
            x_tip = [pt(lm, 8)[0] for lm in frame_landmarks_list if lm is not None]
            if len(x_tip) >= 5:
                x_changes = [x_tip[i+1] - x_tip[i] for i in range(len(x_tip) - 1)]
                side_changes = sum(1 for i in range(len(x_changes) - 1)
                                   if x_changes[i] * x_changes[i+1] < 0)
                if side_changes >= 2:
                    return 'No', 0.75

        # Circular motion with open hand → Stomach pain / Sick
        if all(fingers):  # open hand
            if len(wrist_positions) >= 8:
                x_vals = [p[0] for p in wrist_positions[-8:]]
                y_vals = [p[1] for p in wrist_positions[-8:]]
                x_range = max(x_vals) - min(x_vals)
                y_range = max(y_vals) - min(y_vals)
                # Circular if both x and y have significant range
                if x_range > 0.04 and y_range > 0.04 and direction_changes >= 2:
                    return 'Stomach pain', 0.75

        # Hand moving upward steadily (open palm) → Feeling better
        if all(fingers):
            y_vals = [pt(lm, 0)[1] for lm in frame_landmarks_list if lm is not None]
            if len(y_vals) >= 6:
                # Check consistent upward motion (y decreasing)
                upward_moves = sum(1 for i in range(len(y_vals) - 1) if y_vals[i+1] < y_vals[i])
                if upward_moves >= len(y_vals) * 0.7 and (y_vals[0] - y_vals[-1]) > 0.08:
                    return 'Feeling better', 0.72

        # Fist moving downward → Pain / Hurting
        if not any(fingers[1:]):  # fist-like
            y_vals = [pt(lm, 0)[1] for lm in frame_landmarks_list if lm is not None]
            if len(y_vals) >= 6:
                downward_moves = sum(1 for i in range(len(y_vals) - 1) if y_vals[i+1] > y_vals[i])
                if downward_moves >= len(y_vals) * 0.7 and (y_vals[-1] - y_vals[0]) > 0.08:
                    return 'Pain', 0.72

        # Quick open-close of hand (clenching) → Anxious / Nervous
        finger_states_seq = []
        for lm in frame_landmarks_list:
            if lm is not None:
                fs = self._get_finger_states(lm)
                finger_states_seq.append(sum(fs[1:]))  # count non-thumb fingers
        if len(finger_states_seq) >= 8:
            state_changes = sum(1 for i in range(len(finger_states_seq) - 1)
                               if abs(finger_states_seq[i+1] - finger_states_seq[i]) >= 2)
            if state_changes >= 3:
                return 'Anxious', 0.70

        # Large motion → general "signing detected"
        if avg_motion > 0.05 and max_motion > 0.1:
            return 'signing', 0.50

        return None, 0.0

    # ─── Helpers ────────────────────────────────────────────────────

    def _get_finger_states(self, landmarks):
        """
        Determine which fingers are extended (True) or curled (False).
        Returns (thumb, index, middle, ring, pinky).
        Uses distance-based checks with tolerance for real-world imprecision.
        """
        def pt(i):
            return landmarks[i * 2], landmarks[i * 2 + 1]

        def dist(a, b):
            return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

        wrist = pt(0)
        index_mcp = pt(5)
        pinky_mcp = pt(17)
        palm_center_x = (wrist[0] + index_mcp[0] + pinky_mcp[0]) / 3
        palm_center_y = (wrist[1] + index_mcp[1] + pinky_mcp[1]) / 3

        # THUMB — extended if tip is further from palm center than IP joint
        # Use 2D distance, not just x-axis, so it works in all orientations
        thumb_tip = pt(4)
        thumb_ip = pt(3)
        thumb_mcp = pt(2)
        thumb_tip_dist = dist(thumb_tip, (palm_center_x, palm_center_y))
        thumb_ip_dist = dist(thumb_ip, (palm_center_x, palm_center_y))
        thumb_ext = thumb_tip_dist > (thumb_ip_dist * 1.05)  # small tolerance

        # OTHER FINGERS — tip higher than PIP (y decreases upward in image)
        # Add tolerance: tip must be at least a little above PIP
        # Also check tip-to-MCP distance vs PIP-to-MCP distance as backup
        def finger_extended(tip_idx, pip_idx, mcp_idx):
            tip = pt(tip_idx)
            pip = pt(pip_idx)
            mcp = pt(mcp_idx)
            # Primary: tip.y < pip.y (tip above PIP in image space)
            y_check = tip[1] < (pip[1] + 0.01)  # small tolerance
            # Backup: tip is further from MCP than PIP is (finger reaching out)
            dist_check = dist(tip, mcp) > (dist(pip, mcp) * 0.85)
            return y_check and dist_check

        index_ext = finger_extended(8, 6, 5)
        middle_ext = finger_extended(12, 10, 9)
        ring_ext = finger_extended(16, 14, 13)
        pinky_ext = finger_extended(20, 18, 17)

        return (thumb_ext, index_ext, middle_ext, ring_ext, pinky_ext)

    def _get_finger_angles(self, landmarks):
        """Get angles between finger segments."""
        angles = {}

        def pt(i):
            return np.array([landmarks[i * 2], landmarks[i * 2 + 1]])

        finger_joints = {
            'index': [5, 6, 7, 8],
            'middle': [9, 10, 11, 12],
            'ring': [13, 14, 15, 16],
            'pinky': [17, 18, 19, 20],
        }

        for name, joints in finger_joints.items():
            mcp = pt(joints[0])
            pip = pt(joints[1])
            dip = pt(joints[2])
            tip = pt(joints[3])

            # Angle at PIP joint
            v1 = mcp - pip
            v2 = tip - pip
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
            angles[name] = math.degrees(math.acos(np.clip(cos_angle, -1, 1)))

        return angles

    def close(self):
        """Release MediaPipe resources."""
        self.detector.close()
        self.gesture_recognizer.close()


# Gesture label mapping for UI
GESTURE_LABELS = {
    'open_palm': '🖐️ Open Palm',
    'thumbs_up': '👍 Thumbs Up',
    'thumbs_down': '👎 Thumbs Down',
    'fist': '✊ Fist',
    'peace': '✌️ Peace',
    'pointing': '👉 Pointing',
    'ok_sign': '👌 OK',
    'ily': '🤟 I Love You',
    'horns': '🤘 Rock On',
    'call_me': '🤙 Call Me',
    'pinch': '🤏 Pinch',
    'three_up': '🤟 Three Up',
    'thumb_index_l': '👆 L-Shape',
    'flat_down': '🖐️ Palm Down',
    'four_up': '✋ Four Up',
}

# Default gesture → word mapping (general medical context)
GESTURE_TO_WORD = {
    'open_palm': 'Hello',
    'thumbs_up': 'Yes',
    'thumbs_down': 'Feeling bad',
    'fist': 'No',
    'peace': 'Thank you',
    'pointing': 'There',
    'ok_sign': 'OK',
    'ily': 'I love you',
    'horns': 'Help',
    'call_me': 'Call',
    'pinch': 'Pain',
    'three_up': 'Medicine',
    'thumb_index_l': 'Need',
    'flat_down': 'Please wait',
    'four_up': 'Wait',
}

def get_word_for_gesture(gesture, department=None):
    """Get the standard SASL word for a gesture.

    Gestures have ONE universal meaning regardless of department,
    following South African Sign Language conventions.
    The department parameter is accepted but ignored — meanings are consistent.
    """
    return GESTURE_TO_WORD.get(gesture, gesture)
