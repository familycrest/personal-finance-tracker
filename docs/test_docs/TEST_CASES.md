# Test Case Specification - Personal Budget Tracker

## TDD/Documentation Workflow (reminder)

1. Add a new row in TEST_CASES.md (define test case)
2. Write the test (in tests/)
3. Run the test (expect failure)
4. Write implementation code (just enough to pass)
5. Run the test again (expect success)
6. Update the test case status to PASS or FAIL
7. Document result in TEST_REPORT.md
8. Refactor implementation -> Re-run all tests

## Module: Account Model

| Test ID  | Description                      | Input                                                                         | Expected Output                  | Status |
|----------|----------------------------------|-------------------------------------------------------------------------------|----------------------------------|--------|
| TC-AM-01 | Create valid user account        | username="myusername", password="password123", password_confirm="password123" | Account created successfully     | PASS   |
| TC-AM-02 | Reject username over 150 chars   | username="96Xbsajih4KiJJGBuU98SgQJ6cr0VbKOP3baP6cNnAOG0TxGVS8MHM5tpGcL7lm2t5Yf1mjMi25wtOXPv1DEdu3qksKanNtix9X7jOchRhuSmubmHy4h7iOA0VxUeP3unRY0TOuZEukxjUENM5kHINL                     password="password123", password_confirm="password123"                                                                        | Error raised                     | PASS   |
| TC-AM-03 | Reject invalid type              | type="spending"                                                               | Error raised                     | PASS   |
| TC-AM-04 | Allow optional description       | description not provided                                                      | Transaction created successfully | PASS   |
| TC-AM-05 | Reject empty category variable   | category = ""                                                                 | ValueError raised                | PASS   |


---

## Module: BudgetManager

| Test ID  | Description                        | Input                                               | Expected Output                 | Status |
|----------|------------------------------------|-----------------------------------------------------|----------------------------------|--------|
| TC-BM-01 | Add valid transaction              | Transaction instance                                | Added and stored successfully   |        |
| TC-BM-02 | Get all transactions               | (no input)                                          | List of all transactions        |        |
| TC-BM-03 | Calculate correct balance          | 2 incomes + 3 expenses                              | Correct net total               |        |
| TC-BM-04 | Filter transactions by category    | category="Food"                                     | Only Food transactions returned |        |

---

## Module: DatabaseManager

| Test ID  | Description                        | Input                                               | Expected Output                 | Status |
|----------|------------------------------------|-----------------------------------------------------|----------------------------------|--------|
| TC-DB-01 | Save transaction to database       | Valid Transaction                                   | Record inserted successfully    |        |
| TC-DB-02 | Retrieve transactions from DB      | Query all                                           | Correct data returned           |        |
| TC-DB-03 | Reject duplicate primary key       | Duplicate ID                                        | IntegrityError raised           |        |
| TC-DB-04 | Handle empty DB case               | Empty transaction table                             | Empty list returned             |        |

---

## Module: Transaction Repository

| Test ID    | Description                   | Input                    | Expected Output               | Status |
|------------|-------------------------------|--------------------------|-------------------------------|--------|
| TC-REPO-01 | Add transaction to database   | Valid Transaction object | Transaction saved in database | PASS   |
| TC-REPO-02 | Retrieve transactions from DB | Query all                | Correct data returned         | PASS   |
| TC-REPO-03 | Reject duplicate primary key  | Duplicate ID             | IntegrityError raised         |        |
| TC-REPO-04 | Handle empty DB case          | Empty transaction table  | Empty list returned           |        |

---

## Module: Main App UI

| Test ID  | Description                   | Input                    | Expected Output               | Status |
|----------|-------------------------------|--------------------------|-------------------------------|--------|
| TC-UI-01 | Add transaction to database   | Valid Transaction object | Transaction saved in database | PASS   |
| TC-UI-02 | Retrieve transactions from DB | Query all                | Correct data returned         | PASS   |
| TC-UI-03 | Reject duplicate primary key  | Duplicate ID             | IntegrityError raised         |        |
| TC-UI-04 | Handle empty DB case          | Empty transaction table  | Empty list returned           |        |