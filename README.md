# Linux Lab Environment - Terraform + Docker Kasm

A web-based temporary Linux lab environment that spins up isolated Linux desktops in your browser. Perfect for practicing commands safely without worrying about breaking your system.

## Why This Over Traditional VMs?

- **VMs**: Download ISOs, wait for boot, manage storage, manual cleanup
- **This**: Browser-based, instant access, auto-cleanup, zero configuration

## Tech Stack

- **Quart** - Async Python web framework (Flask alternative)
- **Terraform** - Infrastructure as Code automation
- **Docker Kasm** - Isolated Linux containers with VNC access
- **Asyncio** - Concurrent session management

## Prerequisites

- Python 3.8+
- Docker Desktop (running)
- Terraform CLI
- Git

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd docker-kasm-terraform
```

### 2. Install Python Dependencies

```bash
pip install quart
```

### 3. Verify Docker is Running

```bash
docker --version
docker ps
```

### 4. Verify Terraform Installation

```bash
terraform --version
```

If not installed, download from: https://www.terraform.io/downloads

### 5. Set Up Terraform Configuration

Ensure your `terraform/main.tf` is configured properly with the Kasm Docker provider.

## Usage

### Starting the Application

```bash
python run.py
```

You should see:

```
Initializing Terraform...
Terraform initialized successfully!
 * Running on http://127.0.0.1:5000
```

### Access the Web Interface

Open your browser and navigate to:

```
http://localhost:5000
```

### Using the Lab

1. **Start Lab** - Click "Start Lab" button
2. **Wait for Deployment** - Takes ~30-60 seconds
3. **Get Credentials** - Copy the VNC username and password
4. **Access VNC** - Click the VNC URL to open your Linux desktop
5. **Auto-Cleanup** - Environment destroys itself after 10 minutes
6. **Manual Stop** - Use "Stop Lab" button to end early

## Project Structure

```
.
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration (lifetime, paths)
│   ├── routes/
│   │   └── lab_routes.py        # API endpoints
│   ├── services/
│   │   └── terraform_service.py # Terraform lifecycle & state
│   └── utils/
│       └── terraform_init.py    # Startup initialization
├── templates/
│   └── index.html               # Frontend UI
├── terraform/
│   ├── main.tf                  # Terraform IaC configuration
│   ├── variables.tf             # Input variables
│   └── *.tfstate                # State files (gitignored)
├── run.py                       # Application entry point
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## API Endpoints

| Method | Endpoint         | Description                               |
| ------ | ---------------- | ----------------------------------------- |
| GET    | `/`              | Main web interface                        |
| POST   | `/start`         | Start new lab environment                 |
| GET    | `/status`        | Get current status, logs, and credentials |
| POST   | `/stop`          | Stop running environment                  |
| POST   | `/force-cleanup` | Emergency cleanup (if auto-cleanup fails) |

## Configuration

Edit `app/config.py` to customize:

```python
LAB_LIFETIME = 600  # Session lifetime in seconds (default: 10 minutes)
TERRAFORM_DIR = "./terraform"  # Terraform files directory
```

## How It Works

1. **Initialization** - Terraform initializes once at startup
2. **Start Request** - User clicks "Start Lab"
3. **Provisioning** - Terraform deploys Docker Kasm container
4. **VNC Access** - User connects via browser
5. **Auto-Cleanup** - Environment tears down after timeout
6. **State Management** - Async operations handle concurrent sessions

## Troubleshooting

### Terraform Init Fails

```bash
cd terraform
terraform init
```

### Docker Not Running

```bash
# Windows
Start Docker Desktop

# Verify
docker ps
```

### Port 5000 Already in Use

Change port in `run.py`:

```python
app.run(host="0.0.0.0", port=5001)
```

### Cleanup Stuck

Use the force cleanup endpoint:

```bash
curl -X POST http://localhost:5000/force-cleanup
```

## Development

### Running in Debug Mode

Already enabled in `run.py`:

```python
app.run(debug=True)
```

### Adding New Routes

Add to `app/routes/lab_routes.py`

### Modifying Terraform

Edit `terraform/main.tf` and restart the app

## Production Deployment

For production, use an ASGI server:

```bash
pip install hypercorn
hypercorn run:app --bind 0.0.0.0:8000
```

## Security Notes

- Default VNC password is auto-generated
- Sessions auto-destroy after timeout
- Docker containers are isolated
- Consider adding authentication for production use

## Future Enhancements

- [ ] Multi-user support with session isolation
- [ ] Custom lab templates
- [ ] Persistent storage options
- [ ] User authentication
- [ ] Usage analytics

## License

MIT License

## Contributing

Pull requests welcome! Please ensure:

- Code follows async/await patterns
- Update tests if applicable
- Document new features in README
