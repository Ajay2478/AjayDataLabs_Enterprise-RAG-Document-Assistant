# Deployment Guide

## Overview

The system is deployed using cloud platforms to ensure accessibility and scalability.

Frontend and backend are deployed separately.

---

## Backend Deployment (Railway / Render)

### Steps
1. Create project on platform
2. Connect GitHub repository
3. Set environment variables
4. Configure build command
5. Deploy FastAPI server

### Environment Variables
- GOOGLE_API_KEY
- GROQ_API_KEY

---

## Frontend Deployment (Vercel)

### Steps
1. Connect GitHub repository
2. Select frontend folder
3. Set build command
4. Deploy React application

---

## Local Deployment

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

cd frontend
npm install
npm run dev