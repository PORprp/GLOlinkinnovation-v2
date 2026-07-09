/* Shared database handle using Node's built-in SQLite (Node >= 22.5).
   No native npm build required. */
const path = require('node:path');
const { DatabaseSync } = require('node:sqlite');

const DB_PATH = path.join(__dirname, 'glo.db');
const db = new DatabaseSync(DB_PATH);
// default rollback journal — most portable across filesystems

module.exports = { db, DB_PATH };
