from website import create_app

app = create_app()

if __name__ == 'main':
    app.run(host='0.0.0.0', port=5000)
