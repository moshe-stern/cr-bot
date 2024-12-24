import asyncio
import os
from typing import Any

import requests
from celery.result import AsyncResult
from flask import Blueprint, Response, jsonify, request, send_file, session
from playwright.async_api import async_playwright

from celery_app import celery
from src.celery_tasks import process_update, cleanup_file
from src.classes import CRResource, UpdateType, BillingUpdateKeys
from src.services import update_billings
from src.shared import (
    get_json,
    get_task_progress,
    start,
    handle_dialogs,
    get_cr_session,
)

authorization = Blueprint("authorization", __name__, url_prefix="/authorization")


@authorization.route("", methods=["POST"])
def update() -> tuple[Response, int]:
    data = get_json(request)
    file = data.get("file")
    instance: str = data.get("instance")
    update_type_str: str = data.get("type")
    base64_content: bytes = file.get("$content")
    args = (base64_content, update_type_str, instance)
    task = process_update.apply_async(args=args)
    return jsonify({"task_id": task.id}), 202


@authorization.route("/status/<task_id>", methods=["GET"])
def check_task_status(task_id) -> dict[str, Any]:
    task: AsyncResult = celery.AsyncResult(task_id)
    response: dict[str, Any] = {}
    if task.state == "PENDING":
        response = {
            "state": task.state,
            "progress": get_task_progress(task),
        }
    elif task.state == "SUCCESS":
        response = {
            "state": task.state,
            "file_url": f"/authorization/download/{task_id}",
            "progress": "100%",
        }
    elif task.state == "FAILURE":
        reason = task.info.get("reason")
        task.forget()
        response = {"state": task.state, "fail_reason": reason}
    return response


@authorization.route("/download/<task_id>", methods=["GET"])
def download_file(task_id) -> Response | tuple[Response, int]:
    task = celery.AsyncResult(task_id)
    if task.state == "SUCCESS":
        try:
            if isinstance(task.result, str):
                file_path = task.result
                response = send_file(
                    file_path,
                    as_attachment=True,
                    download_name="updated_file.xlsx",
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            else:
                raise Exception("Task result failed")
            cleanup_file.apply_async((file_path,), countdown=30)
            return response
        except Exception as e:
            return jsonify({"error": f"Error serving file: {str(e)}"}), 500
        finally:
            task.forget()

    elif task.state == "PENDING":
        return jsonify({"error": "Task is still pending"}), 202
    elif task.state == "FAILURE":
        task.forget()
        return jsonify({"error": "Task has failed"}), 400
    else:
        return jsonify({"error": "Task not ready or invalid"}), 400


# for quick testing when adding new services
if os.getenv("DEVELOPMENT") == "TRUE":

    @authorization.route("/test", methods=["POST"])
    def test():
        async def run_test():
            async with async_playwright() as p:
                context = await start(p, "Kadiant")
                cr_session = await get_cr_session()
                res = cr_session.put(
                    "https://members.centralreach.com/crxapi/converted-timesheets/146076506",
                    json={
                        "timesheet": {
                            "timesheetId": 146076506,
                            "organizationContactId": 427999,
                            "schedulingEventId": 422322906,
                            "schedulingCourseId": 93823553,
                            "clientContactId": 428000,
                            "insuranceId": 1949668,
                            "billingId": 427999,
                            "billing": "KADIANT LLC",
                            "status": "Converted",
                            "source": "",
                            "diagnosisCodes": [
                                {"diagnosisCodeId": 21577, "position": 1}
                            ],
                            "segments": [
                                {
                                    "timesheetSegmentId": 156969997,
                                    "providerContactId": 1247996,
                                    "schedulingSegmentId": 542451213,
                                    "serviceDateScheduled": "2021-12-22T00:00:00.0000000Z",
                                    "serviceDate": "2021-12-22T00:00:00+00:00",
                                    "timeZone": "America/Detroit",
                                    "startTimeScheduled": 43200,
                                    "startTime": 43200,
                                    "endTimeScheduled": 44100,
                                    "endTime": 43800,
                                    "driveTimeScheduled": 0,
                                    "driveTime": 0,
                                    "driveMileageScheduled": 0,
                                    "driveMileage": 0,
                                    "procedureCodeIdScheduled": 86771,
                                    "procedureCodeId": 85616,
                                    "serviceNote": "",
                                    "serviceNotePublic": False,
                                    "adminNote": "",
                                    "authorizationId": 16989247,
                                    "serviceLocationId": "45",
                                    "isLocked": True,
                                    "isVoid": False,
                                    "isDeleted": False,
                                    "skipWarnings": False,
                                    "notes":{
                                        "name": "TIMESHEET ATTESTATION",
                                        "description": "Time records must be completely accurate. Please make any corrections necessary so this record is 100% accurate before signing the certification below.\nI hereby attest that the time and hours recorded on this time record accurately and fully identify all time that I have worked during the designated pay period and I did not work any time that was not recorded.  I further acknowledge that I have not violated any policy of the employer during the pay period, including, but not limited to, the employer's policies against working off the clock or unauthorized overtime.\n\nCalifornia, Oregon and Washington residents only: \nI further acknowledge that, except as specified above, I have been provided all meal periods and rest periods to which I am entitled during the pay period, including one duty-free rest period for every four hours of work or major fraction thereof and one duty-free meal period whenever I worked over five hours.\n\nI declare that the foregoing is true and correct under penalty of perjury.\n",
                                        "isRequired": True,
                                        "single": {
                                            "options": [
                                                "Yes"
                                            ],
                                            "index": "0"
                                        },
                                        "answeredOn": "2024-12-18T16:50:30+00:00",
                                        "answeredBy": 1527935,
                                        "billingNoteId": None
                                    },
                                    "rates": [
                                        {
                                            "feeScheduleId": 31274,
                                            "unitsOfService": 1,
                                            "rateProvider": "0.00",
                                            "rateClient": "15.63",
                                            "rateClientAgreed": "15.63",
                                            "rateProviderDriveHourly": "0.000",
                                            "rateProviderDriveMileage": "0.000",
                                            "rateClientDriveHourly": "0.00",
                                            "rateClientDriveMileage": "0.00",
                                        }
                                    ],
                                    "modifiers": [
                                        {"modifier": ""},
                                        {"modifier": ""},
                                        {"modifier": ""},
                                        {"modifier": ""},
                                    ],
                                    "pointers": [{"pointer": 1}],
                                    "signatures": [
                                        {
                                            "signatureIP": "98.242.119.173",
                                            "signatureSource": "",
                                            "signatureName": "james hill",
                                            "signatureType": "Client",
                                            "signatureDate": "2021-12-22T18:01:04.0000000Z",
                                            "signatureContactId": 428000,
                                            "signature": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB2aWV3Qm94PSIwIDAgNTQ5Ljk5OTk4ODA3OTA3MTMgMTg0LjU0NTQ1MDU0NTUzOTY0IiB3aWR0aD0iNTQ5Ljk5OTk4ODA3OTA3MTMiIGhlaWdodD0iMTg0LjU0NTQ1MDU0NTUzOTY0Ij48cGF0aCBkPSJNIDk2LjY0Miw5Ny44NjkgQyA5NC42NDIsMTAwLjM2OSA5NS4wNzcsMTAwLjg3NyA5Mi42NDIsMTAyLjg2OSIgc3Ryb2tlLXdpZHRoPSI1LjM3NyIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSA5Mi42NDIsMTAyLjg2OSBDIDg5LjU3NywxMDUuMzc3IDg5LjM3NCwxMDUuNDcwIDg1LjY0MiwxMDYuODY5IiBzdHJva2Utd2lkdGg9IjQuMTE2IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDg1LjY0MiwxMDYuODY5IEMgODEuMzc0LDEwOC40NzAgODEuMjA4LDEwOC4zNDIgNzYuNjQyLDEwOC44NjkiIHN0cm9rZS13aWR0aD0iMy43NzYiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gNzYuNjQyLDEwOC44NjkgQyA2OC4yMDgsMTA5Ljg0MiA2OC4wOTUsMTEwLjMzOSA1OS42NDIsMTA5Ljg2OSIgc3Ryb2tlLXdpZHRoPSIzLjEwOSIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSA1OS42NDIsMTA5Ljg2OSBDIDUwLjA5NSwxMDkuMzM5IDQ5Ljk0OSwxMDkuMTI2IDQwLjY0MiwxMDYuODY5IiBzdHJva2Utd2lkdGg9IjIuNjk5IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDQwLjY0MiwxMDYuODY5IEMgMzMuNDQ5LDEwNS4xMjYgMzMuMzUwLDEwNS4wMTQgMjYuNjQyLDEwMS44NjkiIHN0cm9rZS13aWR0aD0iMi45MDMiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMjYuNjQyLDEwMS44NjkgQyAxNy4zNTAsOTcuNTE0IDkuMDcyLDEwMC44ODcgOC42NDIsOTEuODY5IiBzdHJva2Utd2lkdGg9IjIuNjQyIiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDguNjQyLDkxLjg2OSBDIDcuMDcyLDU4Ljg4NyA3LjU1Miw0NS4xMDUgMjIuNjQyLDE3Ljg2OSIgc3Ryb2tlLXdpZHRoPSIzLjAyMyIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAyMi42NDIsMTcuODY5IEMgMjguMDUyLDguMTA1IDM2LjI2MiwxNi42MDcgNDkuNjQyLDE3Ljg2OSIgc3Ryb2tlLXdpZHRoPSIyLjM3MyIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSA0OS42NDIsMTcuODY5IEMgNjIuNzYyLDE5LjEwNyA2My4xNTgsMTguOTExIDc1LjY0MiwyMi44NjkiIHN0cm9rZS13aWR0aD0iMi4xODkiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gNzUuNjQyLDIyLjg2OSBDIDgzLjY1OCwyNS40MTEgODMuOTQ0LDI1Ljc4OCA5MC42NDIsMzAuODY5IiBzdHJva2Utd2lkdGg9IjIuNTkxIiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDkwLjY0MiwzMC44NjkgQyA5OC40NDQsMzYuNzg4IDk5LjM4OSwzNi42NzQgMTA0LjY0Miw0NC44NjkiIHN0cm9rZS13aWR0aD0iMi41OTYiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMTA0LjY0Miw0NC44NjkgQyAxMTEuODg5LDU2LjE3NCAxMTIuMDA0LDU2LjgxNCAxMTUuNjQyLDY5Ljg2OSIgc3Ryb2tlLXdpZHRoPSIyLjIxMCIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAxMTUuNjQyLDY5Ljg2OSBDIDEyMC41MDQsODcuMzE0IDExOS42MzMsODcuNzg3IDEyMS42NDIsMTA1Ljg2OSIgc3Ryb2tlLXdpZHRoPSIxLjgzOCIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAxMjEuNjQyLDEwNS44NjkgQyAxMjIuNjMzLDExNC43ODcgMTIyLjYyNCwxMTUuMDI5IDEyMS42NDIsMTIzLjg2OSIgc3Ryb2tlLXdpZHRoPSIyLjM4NCIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAxMjEuNjQyLDEyMy44NjkgQyAxMjEuMTI0LDEyOC41MjkgMTIwLjkzNCwxMjguODU5IDExOC42NDIsMTMyLjg2OSIgc3Ryb2tlLXdpZHRoPSIzLjA4NiIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAxMTguNjQyLDEzMi44NjkgQyAxMTYuOTM0LDEzNS44NTkgMTE2LjE0MiwxMzguMjg2IDExMy42NDIsMTM3Ljg2OSIgc3Ryb2tlLXdpZHRoPSIzLjY1NyIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAxMTMuNjQyLDEzNy44NjkgQyAxMTAuMTQyLDEzNy4yODYgMTEwLjAyNiwxMzQuNDc5IDEwNi42NDIsMTMwLjg2OSIgc3Ryb2tlLXdpZHRoPSI0LjMzNiIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAxMDYuNjQyLDEzMC44NjkgQyAxMDIuNTI2LDEyNi40NzkgMTAyLjM5OSwxMjYuNTY1IDk4LjY0MiwxMjEuODY5IiBzdHJva2Utd2lkdGg9IjMuNjEyIiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDk4LjY0MiwxMjEuODY5IEMgOTQuMzk5LDExNi41NjUgOTQuNTk1LDExNi40MDMgOTAuNjQyLDExMC44NjkiIHN0cm9rZS13aWR0aD0iMy4xOTIiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gOTAuNjQyLDExMC44NjkgQyA4Ny4wOTUsMTA1LjkwMyA4My42NDIsMTA1LjU2MyA4My42NDIsMTAwLjg2OSIgc3Ryb2tlLXdpZHRoPSIzLjE5MSIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSA4My42NDIsMTAwLjg2OSBDIDgzLjY0Miw5Ny4wNjMgODYuNDYyLDk2LjQwNyA5MC42NDIsOTMuODY5IiBzdHJva2Utd2lkdGg9IjMuOTA5IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDkwLjY0Miw5My44NjkgQyAxMDAuNDYyLDg3LjkwNyAxMDAuODI0LDg4LjA0OSAxMTEuNjQyLDgzLjg2OSIgc3Ryb2tlLXdpZHRoPSIyLjUzNyIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAxMTEuNjQyLDgzLjg2OSBDIDEyMi44MjQsNzkuNTQ5IDEyMy4xMjIsODAuMzAxIDEzNC42NDIsNzYuODY5IiBzdHJva2Utd2lkdGg9IjIuMzg4IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDEzNC42NDIsNzYuODY5IEMgMTQ2LjYyMiw3My4zMDEgMTQ2LjUyOSw3Mi44OTggMTU4LjY0Miw2OS44NjkiIHN0cm9rZS13aWR0aD0iMi4yNTAiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMTU4LjY0Miw2OS44NjkgQyAxNjYuNTI5LDY3Ljg5OCAxNjYuNTk1LDY4LjAxOSAxNzQuNjQyLDY2Ljg2OSIgc3Ryb2tlLXdpZHRoPSIyLjc0NCIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAxNzQuNjQyLDY2Ljg2OSBDIDE4MC41OTUsNjYuMDE5IDE4My4zNjQsNjQuMjMwIDE4Ni42NDIsNjUuODY5IiBzdHJva2Utd2lkdGg9IjMuMDU0IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDE4Ni42NDIsNjUuODY5IEMgMTg4LjM2NCw2Ni43MzAgMTgzLjcwOCw3MS40MDIgMTg0LjY0Miw3MS44NjkiIHN0cm9rZS13aWR0aD0iNC4yNjMiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMTg0LjY0Miw3MS44NjkgQyAxODUuNzA4LDcyLjQwMiAxODcuNzg5LDcwLjA2NCAxOTAuNjQyLDY3Ljg2OSIgc3Ryb2tlLXdpZHRoPSI0LjkwOSIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAxOTAuNjQyLDY3Ljg2OSBDIDE5NC4yODksNjUuMDY0IDE5My45OTUsNjQuNjc1IDE5Ny42NDIsNjEuODY5IiBzdHJva2Utd2lkdGg9IjMuOTUyIiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDE5Ny42NDIsNjEuODY5IEMgMjAwLjQ5NSw1OS42NzUgMjAwLjYwMSw1OS44MDUgMjAzLjY0Miw1Ny44NjkiIHN0cm9rZS13aWR0aD0iMy44OTkiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMjAzLjY0Miw1Ny44NjkgQyAyMDYuMTAxLDU2LjMwNSAyMDcuMDg2LDUzLjk4MCAyMDguNjQyLDU0Ljg2OSIgc3Ryb2tlLXdpZHRoPSI0LjA1MyIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAyMDguNjQyLDU0Ljg2OSBDIDIxMC41ODYsNTUuOTgwIDIwOS44ODEsNTguMzE4IDIxMC42NDIsNjEuODY5IiBzdHJva2Utd2lkdGg9IjQuNzE3IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDIxMC42NDIsNjEuODY5IEMgMjExLjM4MSw2NS4zMTggMjEwLjU0Niw2NS41ODEgMjExLjY0Miw2OC44NjkiIHN0cm9rZS13aWR0aD0iNC4xNzAiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMjExLjY0Miw2OC44NjkgQyAyMTIuNTQ2LDcxLjU4MSAyMTIuNjIyLDcxLjg0OSAyMTQuNjQyLDczLjg2OSIgc3Ryb2tlLXdpZHRoPSI0LjEzNyIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAyMTQuNjQyLDczLjg2OSBDIDIxNy42MjIsNzYuODQ5IDIxNy43MDcsNzcuNDIwIDIyMS42NDIsNzguODY5IiBzdHJva2Utd2lkdGg9IjMuODQ3IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDIyMS42NDIsNzguODY5IEMgMjI3LjIwNyw4MC45MjAgMjI3LjU5Myw4MC42OTEgMjMzLjY0Miw4MC44NjkiIHN0cm9rZS13aWR0aD0iMy40OTAiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMjMzLjY0Miw4MC44NjkgQyAyNDQuNTkzLDgxLjE5MSAyNDQuODIyLDgxLjYwMSAyNTUuNjQyLDc5Ljg2OSIgc3Ryb2tlLXdpZHRoPSIyLjYyMCIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAyNTUuNjQyLDc5Ljg2OSBDIDI2OS44MjIsNzcuNjAxIDI2OS43MzYsNzYuNjkzIDI4My42NDIsNzIuODY5IiBzdHJva2Utd2lkdGg9IjIuMTU4IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDI4My42NDIsNzIuODY5IEMgMjg5LjczNiw3MS4xOTMgMjkxLjE5OSw2Ny45MTcgMjk1LjY0Miw2OC44NjkiIHN0cm9rZS13aWR0aD0iMi43NjQiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMjk1LjY0Miw2OC44NjkgQyAyOTguMTk5LDY5LjQxNyAyOTYuOTMwLDcyLjMxMCAyOTcuNjQyLDc1Ljg2OSIgc3Ryb2tlLXdpZHRoPSIzLjk4OCIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAyOTcuNjQyLDc1Ljg2OSBDIDI5OC40MzAsNzkuODEwIDI5Ny4zMjUsODAuMTM2IDI5OC42NDIsODMuODY5IiBzdHJva2Utd2lkdGg9IjMuODY2IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDI5OC42NDIsODMuODY5IEMgMzAwLjMyNSw4OC42MzYgMjk5LjY2OCw5MC4zNjAgMzAzLjY0Miw5Mi44NjkiIHN0cm9rZS13aWR0aD0iMy42NjAiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMzAzLjY0Miw5Mi44NjkgQyAzMDkuMTY4LDk2LjM2MCAzMTAuNjAxLDk1Ljg2OSAzMTcuNjQyLDk1Ljg2OSIgc3Ryb2tlLXdpZHRoPSIzLjgxNSIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAzMTcuNjQyLDk1Ljg2OSBDIDMyNy4xMDEsOTUuODY5IDMyNy4xNjIsOTQuNDg4IDMzNi42NDIsOTIuODY5IiBzdHJva2Utd2lkdGg9IjIuODM1IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDMzNi42NDIsOTIuODY5IEMgMzQ3LjY2Miw5MC45ODggMzQ3LjU5Miw5MC40OTQgMzU4LjY0Miw4OC44NjkiIHN0cm9rZS13aWR0aD0iMi41OTgiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMzU4LjY0Miw4OC44NjkgQyAzNjQuNTkyLDg3Ljk5NCAzNjQuNjQyLDg3Ljg2OSAzNzAuNjQyLDg3Ljg2OSIgc3Ryb2tlLXdpZHRoPSIzLjA0OCIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAzNzAuNjQyLDg3Ljg2OSBDIDM3Ni42NDIsODcuODY5IDM3Ni44NjIsODcuNTg1IDM4Mi42NDIsODguODY5IiBzdHJva2Utd2lkdGg9IjMuMjE1IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDM4Mi42NDIsODguODY5IEMgMzg1Ljg2Miw4OS41ODUgMzg1Ljk1OSw4OS45MDIgMzg4LjY0Miw5MS44NjkiIHN0cm9rZS13aWR0aD0iMy43MDUiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMzg4LjY0Miw5MS44NjkgQyAzOTMuNDU5LDk1LjQwMiAzOTIuNTQyLDk2Ljg1NSAzOTcuNjQyLDk5Ljg2OSIgc3Ryb2tlLXdpZHRoPSIzLjk2NCIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAzOTcuNjQyLDk5Ljg2OSBDIDQwMy41NDIsMTAzLjM1NSA0MDMuOTE4LDEwMy41NzYgNDEwLjY0MiwxMDQuODY5IiBzdHJva2Utd2lkdGg9IjMuMzEwIiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDQxMC42NDIsMTA0Ljg2OSBDIDQxNi45MTgsMTA2LjA3NiA0MTcuMTQyLDEwNC44NjkgNDIzLjY0MiwxMDQuODY5IiBzdHJva2Utd2lkdGg9IjMuMjIzIiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDQyMy42NDIsMTA0Ljg2OSBDIDQyOS4xNDIsMTA0Ljg2OSA0MjkuNDAyLDEwNS45NzIgNDM0LjY0MiwxMDQuODY5IiBzdHJva2Utd2lkdGg9IjMuNDA2IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDQzNC42NDIsMTA0Ljg2OSBDIDQzOC45MDIsMTAzLjk3MiA0MzguOTY0LDEwMy4zNzcgNDQyLjY0MiwxMDAuODY5IiBzdHJva2Utd2lkdGg9IjMuNTk3IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDQ0Mi42NDIsMTAwLjg2OSBDIDQ0OS45NjQsOTUuODc3IDQ0OS43NjUsOTUuNTE5IDQ1Ni42NDIsODkuODY5IiBzdHJva2Utd2lkdGg9IjIuOTU3IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDQ1Ni42NDIsODkuODY5IEMgNDYzLjc2NSw4NC4wMTkgNDYzLjk4OCw4NC4yMjEgNDcwLjY0Miw3Ny44NjkiIHN0cm9rZS13aWR0aD0iMi43MDgiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gNDcwLjY0Miw3Ny44NjkgQyA0NzQuOTg4LDczLjcyMSA0ODAuNjI3LDY3LjE2OCA0NzguNjQyLDY4Ljg2OSIgc3Ryb2tlLXdpZHRoPSIzLjA0MCIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PC9zdmc+",
                                        },
                                        {
                                            "signatureIP": "98.242.119.173",
                                            "signatureSource": "",
                                            "signatureName": "Jessica Demaroc",
                                            "signatureType": "Provider",
                                            "signatureDate": "2021-12-22T18:01:19.0000000Z",
                                            "signatureContactId": 1247996,
                                            "signature": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB2aWV3Qm94PSIwIDAgNTQ5Ljk5OTk4ODA3OTA3MTMgMTg0LjU0NTQ1MDU0NTUzOTY0IiB3aWR0aD0iNTQ5Ljk5OTk4ODA3OTA3MTMiIGhlaWdodD0iMTg0LjU0NTQ1MDU0NTUzOTY0Ij48cGF0aCBkPSJNIDE1NC44MjQsNjIuMzY5IEMgMTU1LjgyNCw2NC44NjkgMTU3LjE3Nyw2NC44OTUgMTU2LjgyNCw2Ny4zNjkiIHN0cm9rZS13aWR0aD0iNS4yNTEiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMTU2LjgyNCw2Ny4zNjkgQyAxNTYuMTc3LDcxLjg5NSAxNTUuOTE3LDcyLjY5NiAxNTIuODI0LDc2LjM2OSIgc3Ryb2tlLXdpZHRoPSI0LjU3MiIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAxNTIuODI0LDc2LjM2OSBDIDE0Ny45MTcsODIuMTk2IDE0Ny41NzQsODIuNjY4IDE0MC44MjQsODYuMzY5IiBzdHJva2Utd2lkdGg9IjMuMjg1IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDE0MC44MjQsODYuMzY5IEMgMTMyLjA3NCw5MS4xNjggMTMxLjcwMCw5MS42NjAgMTIxLjgyNCw5My4zNjkiIHN0cm9rZS13aWR0aD0iMi43NDciIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMTIxLjgyNCw5My4zNjkgQyAxMDUuNzAwLDk2LjE2MCAxMDUuMTM5LDk2LjA2NCA4OC44MjQsOTUuMzY5IiBzdHJva2Utd2lkdGg9IjIuMDM4IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDg4LjgyNCw5NS4zNjkgQyA4MS42MzksOTUuMDY0IDgxLjYzOCw5My44NDcgNzQuODI0LDkxLjM2OSIgc3Ryb2tlLXdpZHRoPSIyLjU5OCIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSA3NC44MjQsOTEuMzY5IEMgNzAuNjM4LDg5Ljg0NyA3MC4xNTMsOTAuMDkzIDY2LjgyNCw4Ny4zNjkiIHN0cm9rZS13aWR0aD0iMy4zODMiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gNjYuODI0LDg3LjM2OSBDIDY0LjY1Myw4NS41OTMgNjMuNjg3LDg1LjEwMCA2My44MjQsODIuMzY5IiBzdHJva2Utd2lkdGg9IjMuOTA5IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDYzLjgyNCw4Mi4zNjkgQyA2NC4xODcsNzUuMTAwIDYzLjkwOSw3My42MzQgNjcuODI0LDY3LjM2OSIgc3Ryb2tlLXdpZHRoPSIzLjg3NiIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSA2Ny44MjQsNjcuMzY5IEMgNzEuNDA5LDYxLjYzNCA3Mi42OTQsNjEuNzc1IDc4LjgyNCw1OC4zNjkiIHN0cm9rZS13aWR0aD0iMy4yNjkiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gNzguODI0LDU4LjM2OSBDIDg2LjE5NCw1NC4yNzUgODYuNjgzLDU0LjkyOCA5NC44MjQsNTIuMzY5IiBzdHJva2Utd2lkdGg9IjIuOTMwIiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDExNy44MjQsNDcuMzY5IEMgMTIyLjgyNCw0Ny4zNjkgMTIyLjg5MSw0Ni44MjEgMTI3LjgyNCw0Ny4zNjkiIHN0cm9rZS13aWR0aD0iNS4wMDAiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMTI3LjgyNCw0Ny4zNjkgQyAxMzEuODkxLDQ3LjgyMSAxMzEuODcxLDQ4LjIwNyAxMzUuODI0LDQ5LjM2OSIgc3Ryb2tlLXdpZHRoPSI0LjE0MiIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAxMzUuODI0LDQ5LjM2OSBDIDE0MC4zNzEsNTAuNzA3IDE0MC43MTUsNTAuMTA5IDE0NC44MjQsNTIuMzY5IiBzdHJva2Utd2lkdGg9IjMuNzU1IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDE0NC44MjQsNTIuMzY5IEMgMTUwLjcxNSw1NS42MDkgMTUwLjM1NSw1Ni4zMjcgMTU1LjgyNCw2MC4zNjkiIHN0cm9rZS13aWR0aD0iMy4yOTAiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMTU1LjgyNCw2MC4zNjkgQyAxNjEuODU1LDY0LjgyNyAxNjIuMTYyLDY0LjQ3OSAxNjcuODI0LDY5LjM2OSIgc3Ryb2tlLXdpZHRoPSIzLjA3MyIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAxNjcuODI0LDY5LjM2OSBDIDE3My4xNjIsNzMuOTc5IDE3Mi45NjMsNzQuMjM4IDE3Ny44MjQsNzkuMzY5IiBzdHJva2Utd2lkdGg9IjMuMDcxIiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDE3Ny44MjQsNzkuMzY5IEMgMTgxLjk2Myw4My43MzggMTgyLjc4MSw4My4yOTggMTg1LjgyNCw4OC4zNjkiIHN0cm9rZS13aWR0aD0iMy4xNjciIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMTg1LjgyNCw4OC4zNjkgQyAxODguNzgxLDkzLjI5OCAxODguNTAyLDkzLjc1MCAxODkuODI0LDk5LjM2OSIgc3Ryb2tlLXdpZHRoPSIzLjI4MCIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAxODkuODI0LDk5LjM2OSBDIDE5MC41MDIsMTAyLjI1MCAxOTAuNTgxLDEwMi41MzAgMTg5LjgyNCwxMDUuMzY5IiBzdHJva2Utd2lkdGg9IjMuODQ5IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDE4OS44MjQsMTA1LjM2OSBDIDE4OC41ODEsMTEwLjAzMCAxODguNDc3LDExMC4zOTAgMTg1LjgyNCwxMTQuMzY5IiBzdHJva2Utd2lkdGg9IjMuNTg0IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDE4NS44MjQsMTE0LjM2OSBDIDE4NC40NzcsMTE2LjM5MCAxODQuMDYzLDExNi4zNTEgMTgxLjgyNCwxMTcuMzY5IiBzdHJva2Utd2lkdGg9IjQuMDQ4IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDE4MS44MjQsMTE3LjM2OSBDIDE3OC41NjMsMTE4Ljg1MSAxNzguNDAxLDExOC45MjIgMTc0LjgyNCwxMTkuMzY5IiBzdHJva2Utd2lkdGg9IjMuOTE5IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDE3NC44MjQsMTE5LjM2OSBDIDE3MC40MDEsMTE5LjkyMiAxNzAuMjA0LDEyMC4xNjYgMTY1LjgyNCwxMTkuMzY5IiBzdHJva2Utd2lkdGg9IjMuNjkwIiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDE2NS44MjQsMTE5LjM2OSBDIDE1OS4yMDQsMTE4LjE2NiAxNTkuMDI0LDExOC4wMjYgMTUyLjgyNCwxMTUuMzY5IiBzdHJva2Utd2lkdGg9IjMuMjEwIiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDE1Mi44MjQsMTE1LjM2OSBDIDE0OC41MjQsMTEzLjUyNiAxNDcuNjI1LDExMy44NzEgMTQ0LjgyNCwxMTAuMzY5IiBzdHJva2Utd2lkdGg9IjMuNDMzIiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDE0NC44MjQsMTEwLjM2OSBDIDE0MS42MjUsMTA2LjM3MSAxNDAuMjMzLDEwNS4yOTcgMTQwLjgyNCwxMDAuMzY5IiBzdHJva2Utd2lkdGg9IjMuNDQwIiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDE0MC44MjQsMTAwLjM2OSBDIDE0MS43MzMsOTIuNzk3IDE0Mi4yMjAsOTAuOTczIDE0Ny44MjQsODUuMzY5IiBzdHJva2Utd2lkdGg9IjMuMDY3IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDE0Ny44MjQsODUuMzY5IEMgMTU1LjcyMCw3Ny40NzMgMTU3LjEwMCw3Ny43NjQgMTY3LjgyNCw3My4zNjkiIHN0cm9rZS13aWR0aD0iMi40NzciIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMTY3LjgyNCw3My4zNjkgQyAxODcuNjAwLDY1LjI2NCAxODcuOTEzLDY1LjA0MyAyMDguODI0LDYwLjM2OSIgc3Ryb2tlLXdpZHRoPSIxLjcyNCIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAyMDguODI0LDYwLjM2OSBDIDIzMC40MTMsNTUuNTQzIDIzMC43MzcsNTUuNzUwIDI1Mi44MjQsNTQuMzY5IiBzdHJva2Utd2lkdGg9IjEuNjUyIiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDI1Mi44MjQsNTQuMzY5IEMgMjcwLjczNyw1My4yNTAgMjcwLjk3OCw1My42ODYgMjg4LjgyNCw1NS4zNjkiIHN0cm9rZS13aWR0aD0iMS43NTUiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMjg4LjgyNCw1NS4zNjkgQyAyOTcuNDc4LDU2LjE4NiAyOTguNjYwLDU1LjA3MSAzMDUuODI0LDU5LjM2OSIgc3Ryb2tlLXdpZHRoPSIyLjMxOSIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAzMDUuODI0LDU5LjM2OSBDIDMxMy42NjAsNjQuMDcxIDMxNC4yNTEsNjUuMzY3IDMxOC44MjQsNzMuMzY5IiBzdHJva2Utd2lkdGg9IjIuNDg1IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDMxOC44MjQsNzMuMzY5IEMgMzIyLjI1MSw3OS4zNjcgMzIwLjQyMCw4MC4zNTAgMzIxLjgyNCw4Ny4zNjkiIHN0cm9rZS13aWR0aD0iMi45MDYiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMzIxLjgyNCw4Ny4zNjkgQyAzMjIuOTIwLDkyLjg1MCAzMjIuMjI5LDkzLjA1MyAzMjMuODI0LDk4LjM2OSIgc3Ryb2tlLXdpZHRoPSIzLjIzMSIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAzMjMuODI0LDk4LjM2OSBDIDMyNS4yMjksMTAzLjA1MyAzMjUuMDk3LDEwMy40MzAgMzI3LjgyNCwxMDcuMzY5IiBzdHJva2Utd2lkdGg9IjMuNDAyIiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDMyNy44MjQsMTA3LjM2OSBDIDMyOS41OTcsMTA5LjkzMCAzMjkuOTg1LDExMC4zMzcgMzMyLjgyNCwxMTEuMzY5IiBzdHJva2Utd2lkdGg9IjMuODU0IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDMzMi44MjQsMTExLjM2OSBDIDMzNS40ODUsMTEyLjMzNyAzMzUuOTQ4LDExMi4wODggMzM4LjgyNCwxMTEuMzY5IiBzdHJva2Utd2lkdGg9IjQuMDE3IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDMzOC44MjQsMTExLjM2OSBDIDM0NS45NDgsMTA5LjU4OCAzNDUuOTgxLDEwOS4yNTkgMzUyLjgyNCwxMDYuMzY5IiBzdHJva2Utd2lkdGg9IjMuMTc3IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDM1Mi44MjQsMTA2LjM2OSBDIDM2OC40ODEsOTkuNzU5IDM2OC42MzMsOTkuOTY1IDM4My44MjQsOTIuMzY5IiBzdHJva2Utd2lkdGg9IjIuMTM3IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDM4My44MjQsOTIuMzY5IEMgMzkyLjYzMyw4Ny45NjUgMzkyLjM0MCw4Ny4zOTcgNDAwLjgyNCw4Mi4zNjkiIHN0cm9rZS13aWR0aD0iMi40NDQiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gNDAwLjgyNCw4Mi4zNjkgQyA0MDUuODQwLDc5LjM5NyA0MDUuNDc2LDc4LjMzOSA0MTAuODI0LDc2LjM2OSIgc3Ryb2tlLXdpZHRoPSIzLjAwNyIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSA0MTAuODI0LDc2LjM2OSBDIDQxNC45NzYsNzQuODM5IDQxNS4zNDcsNzYuMDMzIDQxOS44MjQsNzUuMzY5IiBzdHJva2Utd2lkdGg9IjQuMjA1IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDQxOS44MjQsNzUuMzY5IEMgNDI4Ljg0Nyw3NC4wMzMgNDI5LjEzNyw3NC45MjQgNDM3LjgyNCw3Mi4zNjkiIHN0cm9rZS13aWR0aD0iMi45NjEiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gNDM3LjgyNCw3Mi4zNjkgQyA0NDYuMTM3LDY5LjkyNCA0NDYuMTU2LDY5LjQ3NyA0NTMuODI0LDY1LjM2OSIgc3Ryb2tlLXdpZHRoPSIyLjgyOCIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSA0NTMuODI0LDY1LjM2OSBDIDQ2MC4xNTYsNjEuOTc3IDQ2MC4wNjMsNjEuNjkwIDQ2NS44MjQsNTcuMzY5IiBzdHJva2Utd2lkdGg9IjIuOTE4IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDQ2NS44MjQsNTcuMzY5IEMgNDcyLjA2Myw1Mi42OTAgNDcyLjE1MCw1Mi42ODkgNDc3LjgyNCw0Ny4zNjkiIHN0cm9rZS13aWR0aD0iMi45ODMiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjwvc3ZnPg==",
                                        },
                                    ],
                                    "resources": [],

                                    "sessionNotes": [],

                                }
                            ]
                        }
                    },
                )
                # page = await context.new_page()
                # await handle_dialogs(page)
                # def overide_execptions(req: requests.Request):
                #     if 'https://members.centralreach.com/crxapi/converted-timesheets' in req.url and req.method == 'PUT':
                #
                # page.on('request')
                # resource = CRResource(
                #     id=428000,
                #     updates=BillingUpdateKeys(
                #         start_date='2021-08-09',
                #         end_date='2024-12-18',
                #         insurance_id=2392925,
                #         authorization_name='H2019: Direct Services',
                #         place_of_service="02 - Telehealth Provided Other than in Patient's Home",
                #         service_address="155 Grand Avenue Suite 500 Oakland, CA 94612",
                #     ),
                #     update_type=UpdateType.SCHEDULE,
                # )
                # res = await update_billings(1, 2,[resource], page)
                print(res)
                json = res.json()
                print(json["updateSuccess"])
                return json

        return asyncio.run(run_test())
