import os

def generate_report(log_file, report_name="DLP_Report"):
    """ Generate a report from the logs """
    report_path = f"backend/reports/{report_name}.txt"
    with open(log_file, "r") as log:
        logs = log.readlines()

    with open(report_path, "w") as report:
        report.writelines(logs)
    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    generate_report("backend/logs/usb_activity.log")
