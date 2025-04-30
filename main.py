from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
import aiosqlite

from datetime import datetime



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with aiosqlite.connect("PLMdatabase.db") as con:
        await con.execute("""
        CREATE TABLE IF NOT EXISTS "Design" (
            "ID"	INTEGER,
            "Code Name"	TEXT,
            "Chassis Type"	TEXT,
            "Unit Cost"	INTEGER,
            "Unit Revenue"	INTEGER,
            PRIMARY KEY("ID")
        );
        """)
        await con.commit()
        
        await con.execute("""
        CREATE TABLE IF NOT EXISTS "Team" (
            "ID"	INTEGER,
            "Name"	TEXT,
            "Cash"	INTEGER,
            "Vehicle Design ID"	INTEGER,
            PRIMARY KEY("ID"),
            UNIQUE("Name"),
            FOREIGN KEY("Vehicle Design ID") REFERENCES "Design"("ID")
        );
        """)
        await con.commit()
        
        await con.execute("""
        CREATE TABLE IF NOT EXISTS "Vehicle" (
            "Chassis Serial Number"	TEXT,
            "Team ID"	INTEGER,
            "Purchase Time"	TEXT,
            "Sold Time"	TEXT,
            "Status"	TEXT,
            PRIMARY KEY("Chassis Serial Number"),
            FOREIGN KEY("Team ID") REFERENCES "Team"("ID")
        ); 
        """)
        await con.commit()
    yield

app = FastAPI(lifespan=lifespan, docs_url="/")

async def connect():
    con = await aiosqlite.connect("PLMdatabase.db")
    try:
        yield con
    finally:
        await con.close()
        

class NewChassisPurchase(BaseModel):
    teamName: str
    chassisSerialNum: str
    timeStamp: datetime  = Field(default_factory=datetime.utcnow)


@app.post("/purchases/")
async def new_purchase(
    purchase: NewChassisPurchase,
    con: aiosqlite.Connection = Depends(connect)
    
):
    cur = await con.execute(
        "SELECT ID FROM Team WHERE Name = ?", 
        (purchase.teamName,)
    )
    row = await cur.fetchone()
    if not row:
        raise HTTPException(404, "Team not found")
    team_id = row[0]
    
    purchase_time_str = purchase.timeStamp.strftime("%H:%M:%S")
    await con.execute(
        """
        INSERT INTO Vehicle
          ("Chassis Serial Number","Team ID","Purchase Time","Sold Time","Status")
        VALUES (?, ?, ?, NULL, ?)
        """,
        (purchase.chassisSerialNum, team_id, purchase_time_str, "In Progress")
    )
    await con.commit()
    return {
        "chassisSerialNum": purchase.chassisSerialNum,
        "teamId":           team_id,
        "purchaseTime":     purchase_time_str,
        "status":           "In Progress"
    }




class NewVehicleSale(BaseModel):
    chassisSerialNum: str
    timeStamp: datetime  = Field(default_factory=datetime.utcnow)

@app.post("/sales/")
async def new_sale(
    sale: NewVehicleSale,
    con: aiosqlite.Connection = Depends(connect)
    
):
    cursor = await con.execute(
        'SELECT "Sold Time" FROM "Vehicle" WHERE "Chassis Serial Number" = ?',
        (sale.chassisSerialNum,)
    )
    row = await cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if row[0] is not None:
        raise HTTPException(status_code=400, detail="Vehicle already sold")

    sold_time_str = sale.timeStamp.strftime("%H:%M:%S")

    await con.execute(
        '''
        UPDATE "Vehicle"
           SET "Sold Time" = ?, "Status" = ?
         WHERE "Chassis Serial Number" = ?
        ''',
        (sold_time_str, "Complete", sale.chassisSerialNum)
    )
    await con.commit()
    return {
        "chassisSerialNum": sale.chassisSerialNum,
        "soldTime":         sold_time_str,
        "status":           "Complete"
    }

