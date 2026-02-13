def send_notification(recipient, message, channel="sms"):
    """
    Sends a notification to the user or client.
    
    Args:
        recipient (str): Phone number or ID.
        message (str): The message content.
        channel (str): 'sms' or 'kakao'.
    """
    print(f"[{channel.upper()}] Sending to {recipient}: {message}")
    
    # Placeholder for actual API integration (e.g. Solapi, Twilio, Kakao Biz Message)
    # import requests
    # requests.post(...)
    
    return True

def notify_staff_assignment(site_name, staff_name):
    """Sends a notification when staff is assigned."""
    msg = f"[Field Master Pro] {staff_name}님, '{site_name}' 현장의 담당자로 배정되었습니다."
    send_notification(staff_name, msg, "sms")

def notify_contract_owner(site_name, stage):
    """Sends status update to the client."""
    msg = f"[알림] '{site_name}' 현장의 단계가 '{stage}'(으)로 변경되었습니다."
    send_notification("Client", msg, "kakao")
