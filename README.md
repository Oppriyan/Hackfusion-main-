# Pharmly – AI Powered Smart Pharmacy System

Pharmly is an AI-powered pharmacy assistant designed to automate medicine ordering, inventory management, prescription verification, and pharmacy operations through natural language interaction.

Built during HackFusion Hackathon.

---

## Team Jigglypuff

Team Leader  
Priyanshu Sawant  

Team Members  
Ali Khan  
Shabaz Shaikh  

---

## Problem

Pharmacies still rely on manual systems for:

- Medicine inventory lookup
- Prescription validation
- Order management
- Customer history tracking

This leads to:

- human errors
- slower operations
- compliance risks
- poor patient experience

---

## Solution

Pharmly introduces an **AI agent powered pharmacy system** that enables pharmacists or users to interact using **natural language or voice** to manage pharmacy operations.

Example commands:
order 2 paracetamol check inventory ibuprofen show my order history cancel order 15 upload prescription for amoxicillin
The AI automatically:

- understands intent
- verifies prescription requirements
- checks inventory
- places orders
- returns structured responses

---

## Architecture

Pharmly uses a **4-Layer Agent Architecture**.
### 1. Extractor Layer
Uses Azure OpenAI GPT-4o to convert natural language into structured requests.

Example:"order 2 paracetamol"


becomes
{ intent: "order", medicine_name: "paracetamol", quantity: 2 }
---

### 2. Controller Layer

Handles business logic:

- order validation
- inventory checks
- prescription verification
- order management

This layer connects to backend APIs.

---

### 3. Agent Runner

Orchestrates the agent pipeline:

1. Extract intent
2. Execute controller logic
3. Generate response

---

### 4. Responder Layer

Formats backend results into natural language responses.

Example output:Order ID: 70 Medicine: Paracetamol Quantity: 2 Total Price: €4.12
---

## Tech Stack

Backend

- Python
- Flask
- SQLite

AI

- Azure OpenAI
- GPT-4o model

Automation

- n8n (webhook automation)

Voice AI

- Vapi AI

Observability

- LangSmith

Deployment

- Ngrok (temporary database exposure)

Frontend

- HTML
- CSS
- JavaScript

---

## Key Features

AI Pharmacy Assistant  
Natural language medicine ordering  

Prescription Verification  
Ensures restricted medicines require valid prescriptions  

Inventory Management  
Real-time stock checks  

Order System  
Create, cancel, and track orders  

Voice AI Assistant  
Hands-free pharmacy interaction using Vapi  

Admin Dashboard  
Revenue analytics and inventory monitoring  

---

## Project Structure
agents/ core/ modules / utils / tests 
tools/ tools.py
frontend/ backend/
requirements.txt
.env
---

## Example AI Interaction

User:order 2 paracetamol

AI: Order ID: 70 Medicine: Paracetamol Quantity: 2 Total Price: €4.12

## License

 Project built for HackFusion 3 Hackathon.