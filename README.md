# Product Lifecycle Management System (PLM) – Relational Database Implementation

## Overview
This repository contains the implementation of a **Product Lifecycle Management (PLM) system** designed as part of a consulting-style project for the *Product Design Game* (Grogan and de Weck, 2019). 

The goal of the project was to transition from a spreadsheet-based PLM (Google Sheets) to a **relational database system**. The new system simplifies data management, provides cleaner SQL-based queries, and integrates with HTTP API endpoints to track manufacturing events in real-time.

The system tracks:
- Vehicle designs (code name, chassis type, unit cost, unit revenue)
- Teams and their design selections
- Chassis purchases (with unique serial numbers)
- Completed vehicle sales (with revenue tracking)

---

## Repository Contents
├── ORM.py # ORM model definitions for database schema

├── PLM_database.db # SQLite database file

├── main.py # API implementation (Flask/FastAPI)

└── README.md # Project documentation


# To run the API, use bash command ``python main.py`` in the terminal.
The API will be available at http://localhost:5000.


# Example Usage

Purchase a Chassis: `` POST /purchase_chassis `` 

``` 
Content-Type: application/json

request body:
{
  "team_name": "Team Red",
  "chassis_serial": "A001"
} 
```

 Sell a Vehicle: `` POST /sales ``
 
``` 
Content-Type: application/json

request body:
{
  "chassisSerialNum": "A001"
}
```

---

Group 4

Enci Zheng

Bailey Iannone

Thomas Livingston 

Date: 4/30/2025

