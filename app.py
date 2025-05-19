from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template("index.html")

@app.route('/usb')
def usb():
    return render_template("usb.html")

@app.route('/network')
def network():
    return render_template("network.html")

@app.route('/edr')
def edr():
    return render_template("edr.html")

@app.route('/other')
def other():
    return render_template("other.html")

if __name__ == '__main__':
    app.run(debug=True)
