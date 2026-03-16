from flask import Blueprint, jsonify, request, current_app
import cv2
import numpy as np
import base64
import json
import os
from collections import deque

api_bp = Blueprint('api', __name__)

# ── helpers ───────────────────────────────────────────────────────────────────

def _load_map():
    """Load map.json and return the adjacency dict (cached on app)."""
    if not hasattr(current_app, '_map_data'):
        try:
            with open('map.json', 'r') as f:
                current_app._map_data = json.load(f)
        except Exception:
            current_app._map_data = {}
    return current_app._map_data


def _bfs(graph, start, goal):
    """Return shortest path list from start→goal using BFS, or [] if none."""
    if start == goal:
        return [start]
    if start not in graph:
        return []

    queue   = deque([[start]])
    visited = {start}

    while queue:
        path = queue.popleft()
        node = path[-1]
        for neighbor in graph.get(node, []):
            if neighbor == goal:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return []     # no path found


def _direction_for_next(current, next_node):
    """
    Heuristic: derive a directional hint from label text.
    In a real deployment you would attach compass/bearing metadata to map.json.
    """
    nxt = str(next_node).lower()
    cur = str(current).lower()

    if 'stairs' in nxt:
        return 'go_upstairs',   'Take the stairs'
    if 'lift'   in nxt:
        return 'continue_straight', 'Head to the lift'
    if 'entrance' in nxt or 'main' in nxt:
        return 'continue_straight', 'Head towards the entrance'
    if 'corridor' in nxt:
        # crude: if corridor number > current's corridor → right, else left
        if 'corridor' in cur:
            try:
                cur_n = int(''.join(filter(str.isdigit, cur)))
                nxt_n = int(''.join(filter(str.isdigit, nxt)))
                if nxt_n > cur_n:
                    return 'turn_right', f'Turn right towards {next_node}'
                else:
                    return 'turn_left',  f'Turn left towards {next_node}'
            except ValueError:
                pass
        return 'continue_straight', f'Walk to {next_node}'

    return 'continue_straight', f'Head towards {next_node}'

@api_bp.route('/predict', methods=['POST'])
def predict():
    """API endpoint for model prediction"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        # Make prediction
        predicted_class, confidence = current_app.model_handler.predict(image)
        
        if predicted_class is None:
            return jsonify({'error': 'Prediction failed'}), 500
        
        # Get navigation instruction
        destination = data.get('destination', 'Unknown')
        navigation_instruction = current_app.model_handler.get_navigation_instruction(
            predicted_class, destination
        )
        
        return jsonify({
            'predicted_class': predicted_class,
            'confidence': float(confidence),
            'navigation': navigation_instruction,
            'timestamp': data.get('timestamp')
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

@api_bp.route('/destinations', methods=['GET'])
def get_destinations():
    """Get available destinations"""
    return jsonify({
        'destinations': current_app.config['DESTINATIONS']
    })

@api_bp.route('/entrances', methods=['GET'])
def get_entrances():
    """Get entrance information"""
    return jsonify({
        'entrances': current_app.config['ENTRANCES']
    })

@api_bp.route('/model/status', methods=['GET'])
def model_status():
    """Get model loading status"""
    return jsonify({
        'loaded': current_app.model_handler.is_model_loaded(),
        'type': current_app.model_handler.model_type,
        'labels_count': len(current_app.model_handler.labels),
        'labels': list(current_app.model_handler.labels.values())
    })

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': current_app.model_handler.is_model_loaded(),
        'server': f"{current_app.config['HOST']}:{current_app.config['PORT']}"
    })

@api_bp.route('/path', methods=['GET'])
def get_path():
    """
    BFS pathfinding endpoint.
    Query params:
        from_loc  – current detected room label (e.g. "511A")
        to_loc    – destination room label      (e.g. "HOD")
    Returns:
        path        – full list of nodes from start to goal
        next_step   – immediate next node to walk towards
        action      – directional action string for the overlay
        message     – human-readable instruction
        steps_left  – how many hops remain
    """
    start = request.args.get('from_loc', '').strip()
    goal  = request.args.get('to_loc',   '').strip()

    if not start or not goal:
        return jsonify({'error': 'Both from_loc and to_loc are required'}), 400

    if start == goal:
        return jsonify({
            'path': [start],
            'next_step': start,
            'action': 'destination_reached',
            'message': f"You've arrived at {goal}!",
            'steps_left': 0
        })

    graph = _load_map()
    path  = _bfs(graph, start, goal)

    if not path:
        return jsonify({
            'error': f"No path found from '{start}' to '{goal}'",
            'path': []
        }), 404

    next_node           = path[1] if len(path) > 1 else goal
    action, message     = _direction_for_next(start, next_node)

    # If the very next step IS the destination, celebrate
    if next_node == goal:
        action  = 'destination_reached'
        message = f"You've arrived at {goal}!"

    return jsonify({
        'path':       path,
        'next_step':  next_node,
        'action':     action,
        'message':    message,
        'steps_left': len(path) - 1
    })