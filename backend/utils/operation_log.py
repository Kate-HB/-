from flask import request
from models import db
from models.system import OperationLog
from utils.auth import get_current_employee_id
import sys


def log_operation(module, operation, target_type=None, target_id=None,
                  target_name=None, details=None):
    try:
        emp_id = get_current_employee_id()
        log = OperationLog(
            operator_id=emp_id,
            module=module,
            operation=operation,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            details=details,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        print(f'[OperationLog] {module}/{operation} {target_type}#{target_id} by emp#{emp_id} OK', file=sys.stderr)
    except Exception as e:
        print(f'[OperationLog ERROR] {e}', file=sys.stderr)
        import traceback
        traceback.print_exc()
