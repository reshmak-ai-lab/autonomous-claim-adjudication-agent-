Autonomous Claim Adjudication & Fraud Detection Agent, is  a multi-stage agentic workflow.

Agents/components used in your project
Agent / Component	Main Responsibility	Example
📄 Document Processing Agent	Reads and classifies claim/medical documents	PDF, TXT, medical reports, bills
🔐 Privacy / PII Agent	Detects and redacts sensitive information	Aadhaar, PAN, ABHA, phone, address
🏥 Clinical Extraction Agent	Extracts medical information	Diagnosis, treatment, procedures
💰 Billing Extraction Agent	Extracts financial information	Hospital bill, claimed amount, line items
📚 Policy Retrieval Agent	Finds relevant policy clauses using RAG	Coverage, exclusions, waiting periods
🧠 Memory / Claim History Agent	Retrieves previous claim/patient context	Previous claims, utilization
⚖️ Rule Evaluation Agent	Applies deterministic insurance rules	Room rent, copay, deductible, exclusions
🧮 Financial Calculation Agent	Calculates eligible and payable amounts	Deductions and final payable
🕵️ Fraud Detection Agent	Identifies suspicious claim patterns	Repeated claims, inconsistencies
🔎 Document Consistency Agent	Checks whether claim documents agree	Dates, diagnosis, billing inconsistencies
🛠️ Tool/MCP Agent	Calls specialized external/internal tools	Tariff, ICD-10, calculation services
🤖 Adjudication Agent	Combines all evidence and determines outcome	APPROVED / PARTIAL / REJECTED
🛡️ Guardrail/Validation Layer	Validates the final decision and safety conditions	Schema validation, human-review override
The important distinction

The core agents as:

                    CLAIM
                      │
                      ▼
          ┌─────────────────────┐
          │ Document Processing │
          │      Agent          │
          └──────────┬──────────┘
                     ▼
          ┌─────────────────────┐
          │ Privacy / PII Agent │
          └──────────┬──────────┘
                     ▼
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
   Clinical       Billing       Document
   Extraction     Extraction    Validation
      Agent          Agent          Agent
       │             │             │
       └─────────────┼─────────────┘
                     ▼
          ┌─────────────────────┐
          │  Policy RAG Agent   │
          └──────────┬──────────┘
                     │
              ┌──────┴──────┐
              ▼             ▼
        Memory Agent    Fraud Agent
              │             │
              └──────┬──────┘
                     ▼
          ┌─────────────────────┐
          │   Rule Evaluation   │
          │       Agent         │
          └──────────┬──────────┘
                     ▼
          ┌─────────────────────┐
          │ Financial Calculation│
          │       Agent         │
          └──────────┬──────────┘
                     ▼
          ┌─────────────────────┐
          │ Adjudication Agent  │
          └──────────┬──────────┘
                     ▼
             Guardrails / Review
                     ▼
          FINAL CLAIM DECISION

Architecture uses:

LLM reasoning + RAG + deterministic rules + memory + MCP tools + fraud detection + guardrails

Streamlit page to have only these two main sections
So the top-level Streamlit layout should effectively be:

# Autonomous Claim Adjudication & Fraud Detection

📋 Claim Adjudication
    ├── Claim Input
    ├── Policy Validation
    ├── Financial Calculation
    ├── Fraud & Document Risk
    ├── Policy Evidence
    └── Final Adjudication

🧪 Testing
    ├── Unit Testing
    ├── Integration Testing
    └── Evaluation Testing

the claim adjudication output can give detailed information, not just APPROVED / REJECTED.

A useful adjudication result should include:

Section	Details
Claim Information	Claim ID, patient ID, policy ID, claim date
Claimed Amount	Total amount submitted by the claimant
Eligible Amount	Amount payable after policy/rule validation
Decision	APPROVED, PARTIAL_APPROVAL, REJECTED, or HUMAN_REVIEW
Policy Validation	Policy active/inactive, coverage applicability
Coverage Check	Whether treatment/procedure is covered
Waiting Period	PED/waiting-period validation
Room Rent	Room-rent limit and proportional deduction
Copay	Applicable copayment
Deductible	Deductible applied
Non-payable Items	Items excluded from reimbursement
Sum Insured	Available balance and amount consumed
Fraud Assessment	Fraud risk and detected indicators
Document Validation	Missing/inconsistent/valid documents
RAG Evidence	Policy clauses used to make the decision
Reasoning	Explanation of why the claim received the decision
Final Payable	Amount recommended for payment
Human Review	Whether manual intervention is required


This should be a separate section, not part of Claim Adjudication.

Inside Testing, we can have:

Testing Type	Purpose
Unit Testing	Test individual modules/rules
Integration Testing	Test MCP, memory, RAG, and service integration
Evaluation Testing	Test end-to-end claim decisions against expected results



