import connect, {sql} from '@databases/sqlite';
const db = connect();

console.log('Creating persistence');

let currentTrackingId = 0;
async function prepare() {
    await db.query(sql`
      CREATE TABLE tracking_event (
        id INTEGER NOT NULL PRIMARY KEY,
        orderId VARCHAR NOT NULL,
        stationId INTEGER,
        startTime INTEGER,
        endTime INTEGER
      );
    `);

    await db.query(sql`
      CREATE TABLE station_name (
        stationId INTEGER NOT NULL PRIMARY KEY,
        stationName VARCHAR NOT NULL
      )
    `);

    await db.query(sql`
        INSERT INTO station_name (stationId, stationName)
        VALUES (1, "Milling")
    `);

    await db.query(sql`
        INSERT INTO station_name (stationId, stationName)
        VALUES (2, "Polishing")
    `);

    await db.query(sql`
        INSERT INTO station_name (stationId, stationName)
        VALUES (3, "Assembly")
    `);

    await db.query(sql`
        INSERT INTO station_name (stationId, stationName)
        VALUES (4, "Conservation")
    `);
      
}

const prepared = prepare();



export async function setTrackingStart(orderId, stationId, startTime) {
    await prepared;
    await db.query(sql`
      INSERT INTO tracking_event (id, orderId, stationId, startTime)
        VALUES (${currentTrackingId++}, ${orderId}, ${stationId}, ${startTime})
    `
    //  ON CONFLICT (id) DO UPDATE
    //    SET value=excluded.value;
    //`
    );
}

export async function setTrackingEnd(orderId, stationId, endTime) {
    await prepared;
    await db.query(sql`
      UPDATE tracking_event
        SET endTime=${endTime}
        WHERE orderId=${orderId}
            AND stationId=${stationId}
            AND endTime IS NULL
    `
    //  ON CONFLICT (id) DO UPDATE
    //    SET value=excluded.value;
    //`
    );
}

export async function getStationAggregates() {
    await prepared;
    const result = await db.query(sql`
        SELECT timeSums.stationId, sn.stationName as stationName, AVG(timeSums.timeDiff) AS stationThroughput
            FROM (
                SELECT stationId, endTime - startTime AS timeDiff
                FROM tracking_event
                WHERE endTime IS NOT NULL
            ) AS timeSums
            LEFT JOIN station_name AS sn ON sn.stationId = timeSums.stationId
            GROUP BY timeSums.stationId
    `);

    return result;
}

export async function readTrackingEvents() {
    await prepared;
    const results = await db.query(sql`
        SELECT * FROM tracking_event;
    `);

    return results ? results : [];
}