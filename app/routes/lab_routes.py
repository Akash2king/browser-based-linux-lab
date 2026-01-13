import asyncio
from quart import Blueprint, jsonify, render_template
from app.services.terraform_service import (
    lab_state, 
    terraform_lifecycle, 
    force_destroy
)

bp = Blueprint('lab', __name__)


@bp.route("/")
async def home():
    """Render the home page"""
    return await render_template("index.html")


@bp.route("/start", methods=["POST"])
async def start():
    """Start a new lab environment"""
    lab_state.reset()
    asyncio.create_task(terraform_lifecycle())
    return jsonify({"status": "started"})


@bp.route("/status")
async def status():
    """Get current lab status"""
    return jsonify({
        "state": lab_state.execution_state,
        "logs": lab_state.execution_log,
        "remaining_seconds": lab_state.get_remaining_time(),
        "vm_url": lab_state.vm_url,
        "credentials": lab_state.vm_creds if lab_state.execution_state == "RUNNING" else None
    })


@bp.route("/stop", methods=["POST"])
async def stop():
    """Stop the running lab environment"""
    if lab_state.execution_state == "RUNNING":
        lab_state.execution_state = "STOPPING"
        lab_state.log("Manual stop requested by user")
        return jsonify({
            "status": "stopping", 
            "message": "Lab environment is being stopped"
        })
    else:
        return jsonify({
            "status": "error", 
            "message": f"Cannot stop in {lab_state.execution_state} state"
        })


@bp.route("/force-cleanup", methods=["POST"])
async def force_cleanup():
    """Emergency cleanup endpoint for failed destroy operations"""
    try:
        await force_destroy()
        return jsonify({
            "status": "success", 
            "message": "Cleanup completed"
        })
    except Exception as e:
        lab_state.log(f"Force cleanup error: {str(e)}")
        lab_state.execution_state = "IDLE"
        return jsonify({
            "status": "partial", 
            "message": "Reset to IDLE state. Check Docker manually."
        })
