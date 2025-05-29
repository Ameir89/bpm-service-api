# application/seeder_api/seeder.py
import json
import config as app
from . import seeder_api_blueprint
from flask import request, jsonify
from application.common.seeder_control import SeedController


@seeder_api_blueprint.route('/api/auth/seeder', methods=['GET'])
def seeder():
    result = SeedController.save_data()
    return jsonify({'message': result}), 200


@seeder_api_blueprint.errorhandler(403)
def forbidden(e):
    return jsonify({
        "message": "Forbidden",
        "error": str(e),
        "data": None,
        "success": False
    }), 403

@seeder_api_blueprint.errorhandler(404)
def forbidden(e):
    return jsonify({
        "message": "Endpoint Not Found",
        "error": str(e),
        "data": None,
        "success": False
    }), 404
