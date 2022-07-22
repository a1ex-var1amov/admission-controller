from flask import Flask, request, jsonify
from os import environ
import logging

webhook = Flask(__name__)

webhook.config['LABEL'] = environ.get('LABEL')
webhook.config['VALUE'] = environ.get('VALUE')

webhook.logger.setLevel(logging.INFO)

if "LABEL" not in environ:
    webhook.logger.error("Required environment variable for label isn't set. Exiting...")
    exit(1)

if "VALUE" not in environ:
    webhook.logger.error("Required environment variable for label isn't set. Exiting...")
    exit(1)

@webhook.route('/validate', methods=['POST'])

def validating_webhook():

    request_info = request.get_json()

    webhook.logger.info(f'The request body is {request_info}')

    uid = request_info["request"].get("uid")
    meta = request_info["request"]["oldObject"]["metadata"]
    kind = request_info["request"]["oldObject"]["kind"]

    name = meta["name"]
    
    key = 'labels'

    label_k = webhook.config['LABEL']
    label_v = webhook.config['VALUE']

    if key in meta.keys():
        webhook.logger.info(f'labels are applied. checking')
        if label_k in meta["labels"]:
            if label_v in meta["labels"][label_k]:
                webhook.logger.info(f'{meta["labels"][label_k]} OLOLO')
                return admission_response(True, uid, f"{label_k} label exists.")
            else:
                webhook.logger.info(f'{kind}/{name} has the required label \"{label_k}\", but the value is wrong. Ignoring')
                return admission_response(False, uid, f'{kind}/{name} has the \"{label_k}\" label, but the value is wrong. Please change the value to \"{label_v}\" to delete this {kind}')
        else:
            webhook.logger.error(f'{kind}/{name} has no the required label. Request denied')
            return admission_response(False, uid, f'{kind}/{name} has no the required label. Please set label \"{label_k}={label_v}\" to delete this {kind}')
    else:
        webhook.logger.info(f'{kind}/{name} has no labels. Ignorring')
        return admission_response(False, uid, f"The label \"{label_k}={label_v}\" must be set")


def admission_response(allowed, uid, message):
    return jsonify({"apiVersion": "admission.k8s.io/v1",
                    "kind": "AdmissionReview",
                    "response":
                        {"allowed": allowed,
                         "uid": uid,
                         "status": {"message": message}
                         }
                    })


if __name__ == '__main__':
    webhook.run(host='0.0.0.0',
                port=5000)
