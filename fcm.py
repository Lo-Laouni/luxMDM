from pyfcm import FCMNotification

push_service = FCMNotification(api_key="AIzaSyAuZilyheSPFuArg0Z3ZEZ4X6IzbWTyv58")

registrationID = "deviceRegistrationID"  # device registration_token (refreshed tokens)

data_message = {
    'decommission': 'true',
    'wipe': 'true'
}

result = push_service.notify_single_device(registration_id=registrationID, data_message=data_message)

# Response from FCM Server.
multicast_id = result['multicast_id']  # Unique ID (number) identifying the multicast message.
Success = result['success']  # Number of m essages that were processed without an error.
failure = result['failure']  # Number of messages that could not be processed.
canonical_ids = result['canonical_ids']  # Number of results that contain a canonical registration token.
results = result['results']  # Array of objects representing the status of the messages processed.