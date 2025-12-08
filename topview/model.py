# backend/topview/model.py

from ultralytics import YOLO
import numpy as np
import cv2
import base64

class TopViewModel:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_trees(self, img):
        results = self.model.predict(img, conf=0.25, imgsz=640, verbose=False)
        r = results[0]

        boxes = []
        centroids = []

        for box in r.boxes:
            xyxy = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0].cpu().numpy())
            x1, y1, x2, y2 = map(int, xyxy.tolist())

            width = x2 - x1
            height = y2 - y1
            if width < 300 or height < 300:
                continue

            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            boxes.append({
                "x1": x1, "y1": y1, 
                "x2": x2, "y2": y2,
                "cx": cx, "cy": cy,
                "conf": round(conf, 3)
            })

        return boxes


def assign_numbers(centroids, img_height, row_eps_px=None):
    """
    Assigns tree numbers to centroids based on spatial layout (row-major ordering).
    Uses improved clustering to properly group trees into rows and columns.
    centroids: list of dicts with 'cx' and 'cy'
    img_height: height of image for threshold calculation
    row_eps_px: optional threshold for grouping rows (pixels)
    Returns: centroids with added 'tree_number' field
    """
    if not centroids:
        return []

    if row_eps_px is None:
        # More adaptive threshold based on image height
        row_eps_px = max(30, int(img_height * 0.08))

    # Sort by y-coordinate to identify rows
    centroids_sorted = sorted(centroids, key=lambda c: c["cy"])
    
    # Improved row clustering using dynamic threshold
    rows = []
    current_row = [centroids_sorted[0]]
    
    for c in centroids_sorted[1:]:
        # Check if this point belongs to current row
        avg_y = sum(p["cy"] for p in current_row) / len(current_row)
        if abs(c["cy"] - avg_y) <= row_eps_px:
            current_row.append(c)
        else:
            # New row detected
            rows.append(sorted(current_row, key=lambda p: p["cx"]))  # Sort by x within row
            current_row = [c]
    
    # Don't forget the last row
    if current_row:
        rows.append(sorted(current_row, key=lambda p: p["cx"]))

    # Assign numbers: left-to-right, top-to-bottom
    numbered = []
    num = 1
    for row in rows:
        for c in row:
            c["tree_number"] = num
            numbered.append(c)
            num += 1
    
    return numbered


def draw_overlay(img, centroids, out_path=None, pin_radius=60):
    """
    Draws large numbered pins on the image at centroid locations with health-based colors.
    img: input image (numpy array)
    centroids: list of dicts with 'cx', 'cy', 'tree_number', and optional 'final_status'
    out_path: optional path to save the annotated image
    pin_radius: radius of the pin circle (default 60 for large visible pins)
    Returns: annotated image
    """
    out = img.copy()
    
    # First pass: draw all circles
    for c in centroids:
        x, y = int(c["cx"]), int(c["cy"])
        status = c.get("final_status", "healthy")
        
        # Determine color based on health status
        if status == "critical" or c.get("critical_alert", False):
            color = (0, 0, 255)  # Red
        elif status == "unhealthy":
            color = (0, 165, 255)  # Orange
        else:
            color = (0, 255, 0)  # Green (healthy)
        
        # Draw circle with thick black outline for visibility
        cv2.circle(out, (x, y), pin_radius + 4, (0, 0, 0), thickness=8, lineType=cv2.LINE_AA)
        cv2.circle(out, (x, y), pin_radius, color, thickness=-1, lineType=cv2.LINE_AA)
    
    # Second pass: draw text with collision avoidance
    used_regions = []  # Store (x1, y1, x2, y2) of text boxes
    
    for c in centroids:
        x, y = int(c["cx"]), int(c["cy"])
        num = c.get("tree_number", "")
        
        # Calculate text size
        font_scale = pin_radius / 20.0
        thickness = max(2, int(pin_radius / 10))
        text_size = cv2.getTextSize(str(num), cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
        text_w, text_h = text_size
        
        # Try different positions (center, above, below, left, right)
        positions = [
            (x - text_w // 2, y + text_h // 2),  # Center (default)
            (x - text_w // 2, y - pin_radius - text_h - 10),  # Above
            (x - text_w // 2, y + pin_radius + text_h + 10),  # Below
            (x + pin_radius + 10, y + text_h // 2),  # Right
            (x - pin_radius - text_w - 10, y + text_h // 2),  # Left
        ]
        
        text_x, text_y = positions[0]  # Default to center
        text_box = (text_x - 5, text_y - text_h - 5, text_x + text_w + 5, text_y + 5)
        
        # Check for collision with existing text
        collision = False
        for used_box in used_regions:
            if not (text_box[2] < used_box[0] or text_box[0] > used_box[2] or
                    text_box[3] < used_box[1] or text_box[1] > used_box[3]):
                collision = True
                break
        
        # If collision, try alternative positions
        if collision:
            for alt_x, alt_y in positions[1:]:
                alt_box = (alt_x - 5, alt_y - text_h - 5, alt_x + text_w + 5, alt_y + 5)
                alt_collision = False
                for used_box in used_regions:
                    if not (alt_box[2] < used_box[0] or alt_box[0] > used_box[2] or
                            alt_box[3] < used_box[1] or alt_box[1] > used_box[3]):
                        alt_collision = True
                        break
                if not alt_collision:
                    text_x, text_y = alt_x, alt_y
                    text_box = alt_box
                    break
        
        # Draw text with black outline for better visibility
        cv2.putText(out, str(num), (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
        cv2.putText(out, str(num), (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
        
        # Store this text region
        used_regions.append(text_box)
    
    if out_path:
        cv2.imwrite(out_path, out)
    return out
