from win10toast import ToastNotifier

def notify_user(message):
    toaster = ToastNotifier()
    toaster.show_toast("DLP Alert", message, duration=5, threaded=True)
