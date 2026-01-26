/**
 * SQLite Database Connection (sql.js)
 * COT Pulse Backend
 */

const initSqlJs = require('sql.js');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

// Database file path
const dataDir = path.join(__dirname, 'data');
const dbPath = path.join(dataDir, 'cotpulse.db');

let db = null;
let SQL = null;

/**
 * Initialize the database
 */
async function initDatabase() {
    if (db) return db;

    // Ensure data directory exists
    if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, { recursive: true });
    }

    // Initialize SQL.js
    SQL = await initSqlJs();

    // Load existing database or create new one
    if (fs.existsSync(dbPath)) {
        const fileBuffer = fs.readFileSync(dbPath);
        db = new SQL.Database(fileBuffer);
        console.log(`[Database] Loaded existing database: ${dbPath}`);
    } else {
        db = new SQL.Database();
        console.log(`[Database] Created new database: ${dbPath}`);
    }

    return db;
}

/**
 * Save database to file
 */
function saveDatabase() {
    if (!db) return;
    const data = db.export();
    const buffer = Buffer.from(data);
    fs.writeFileSync(dbPath, buffer);
}

/**
 * Get the database instance
 */
function getDb() {
    if (!db) {
        throw new Error('Database not initialized. Call initDatabase() first.');
    }
    return db;
}

/**
 * Run a query that modifies data (INSERT, UPDATE, DELETE)
 */
function run(sql, params = []) {
    const database = getDb();
    database.run(sql, params);
    saveDatabase();
}

/**
 * Get a single row
 */
function get(sql, params = []) {
    const database = getDb();
    const stmt = database.prepare(sql);
    stmt.bind(params);

    if (stmt.step()) {
        const row = stmt.getAsObject();
        stmt.free();
        return row;
    }
    stmt.free();
    return undefined;
}

/**
 * Get all rows
 */
function all(sql, params = []) {
    const database = getDb();
    const stmt = database.prepare(sql);
    stmt.bind(params);

    const rows = [];
    while (stmt.step()) {
        rows.push(stmt.getAsObject());
    }
    stmt.free();
    return rows;
}

/**
 * Execute raw SQL (for schema changes)
 */
function exec(sql) {
    const database = getDb();
    database.exec(sql);
    saveDatabase();
}

/**
 * Test database connection
 */
async function testConnection() {
    try {
        await initDatabase();
        const result = get('SELECT 1 as test');
        console.log(`[Database] Connection test successful`);
        return true;
    } catch (error) {
        console.error('[Database] Connection test failed:', error.message);
        return false;
    }
}

/**
 * Check if database has been initialized with tables
 */
function isInitialized() {
    try {
        const result = get("SELECT name FROM sqlite_master WHERE type='table' AND name='users'");
        return !!result;
    } catch (error) {
        return false;
    }
}

module.exports = {
    initDatabase,
    getDb,
    run,
    get,
    all,
    exec,
    saveDatabase,
    testConnection,
    isInitialized,
    dbPath
};
