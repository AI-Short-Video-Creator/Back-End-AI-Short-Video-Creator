from flask import Blueprint, jsonify
from app.sample_bp.service import SampleService

class SampleController:
    def __init__(self):
        self.service = SampleService()
        self.sample_bp = Blueprint('sample_bp', __name__)

        self._register_routes()

    def _register_routes(self):
        self.sample_bp.add_url_rule('/', view_func=self.sample, methods=['GET'])

    def sample(self):
        """Sample route handler."""
        # Call the service method to get data
        data = self.service.sample()
        return jsonify({"data": data}), 200
    
# Create an instance of SampleRoute
sample_controller = SampleController()
sample_bp = sample_controller.sample_bp    