## SETUP
1. Have python3 installed.
2. Clone the project.
3. Type `pip3 install -r requirements.txt`
4. Start Server `python3 manage.py runserver`.

## PROGRESS

Tier1 (permission 1)

- [ ] open accounts
- [ ] initiate fund deposit
- [ ] view, decline, authorize non-critical request
- [ ] modify personal account

Tier2 (permission 2)

- [ ] Approve critical transaction (above $1000).
- [ ] view, decline, authorize non-critical request
- [ ] view, decline, authorize critical request
- [ ] modify personal account
- [ ] view and modify internal users’ accounts

Admin (permission 3)

- [ ] Create, update and delete Tie1 and tie2.
- [ ] view, create, modify, and delete internal users’ account
- [ ] access the system log file
- [ ] access PII

Individual User (permission 0)

Merchant/Organization (permission 0)

Request

- [ ] fund transfer
- [ ] payment request
- [ ] account modification request
- [ ] account opening request
