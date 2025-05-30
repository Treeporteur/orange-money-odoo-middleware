from flask import Flask, request, jsonify, redirect, render_template_string
import requests
import json
import time
import uuid
import hashlib
from datetime import datetime

app = Flask(__name__)

# Configuration mock
DEVELOPMENT_MODE = True
mock_payments = {}
mock_tokens = {}
