from flask import Blueprint, render_template, request, redirect, url_for, current_app

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main landing page - can detect entrance from QR code"""
    entrance_id = request.args.get('entrance', 1, type=int)

    # Validate entrance ID
    if entrance_id not in range(1, current_app.config['ENTRANCE_COUNT'] + 1):
        entrance_id = 1

    entrance_info = current_app.config['ENTRANCES'].get(entrance_id, {
        'name': f'Entrance {entrance_id}',
        'description': f'Building entrance {entrance_id}'
    })

    # Use updated DESTINATIONS from config
    destinations = current_app.config.get('DESTINATIONS', [])

    return render_template(
        'index.html',
        entrance_id=entrance_id,
        entrance_info=entrance_info,
        destinations=destinations
    )

@main_bp.route('/destination')
def destination_select():
    """Destination selection page"""
    entrance_id = request.args.get('entrance', 1, type=int)

    # Load map destinations from memory (Optimized)
    map_data = current_app.config.get('MAP_DATA', {})
    map_values = list(map_data.values()) if map_data else []

    # Load model labels if available
    labels = getattr(current_app.model_handler, "labels", [])

    return render_template(
        'destination_select.html',
        entrance_id=entrance_id,
        map_keys=map_values,
        labels=labels
    )

@main_bp.route('/navigate')
def navigate():
    """AR Navigation page"""
    destination = request.args.get('destination', 'Unknown')
    entrance_id = request.args.get('entrance', 1, type=int)

    # Validate destination against config DESTINATIONS
    destinations = current_app.config.get('DESTINATIONS', [])
    if destination not in destinations:
        return redirect(url_for('main.destination_select', entrance=entrance_id))

    # Get entrance info for template
    entrance_info = current_app.config['ENTRANCES'].get(entrance_id, {
        'name': f'Entrance {entrance_id}',
        'description': f'Building entrance {entrance_id}'
    })

    return render_template(
        'navigation.html',
        destination=destination,
        entrance_id=entrance_id,
        entrance_info=entrance_info
    )

@main_bp.route('/qr-codes')
def qr_codes():
    """Display QR codes for printing"""
    return render_template(
        'qr_codes.html',
        entrances=current_app.config['ENTRANCES']
    )

@main_bp.route('/status')
def status():
    """System status page"""
    model_status = {
        'loaded': current_app.model_handler.is_model_loaded(),
        'type': current_app.model_handler.model_type,
        'labels_count': len(current_app.model_handler.labels)
    }

    return render_template(
        'status.html',
        model_status=model_status,
        config=current_app.config
    )