/* Seed the SQLite database with schema + sample tickets.
   Run:  npm run seed   (or  node db/seed.js)
   Uses Node's built-in node:sqlite (Node >= 22.5). */
const fs = require('node:fs');
const path = require('node:path');
const { db, DB_PATH } = require('./db');

// apply schema
db.exec(fs.readFileSync(path.join(__dirname, 'schema.sql'), 'utf8'));

// demo user with a bound bank account
db.prepare(`INSERT OR REPLACE INTO users (id,name,bank_name,bank_account,pin_hash)
  VALUES (?,?,?,?,?)`).run('0812345678', 'นายสลาก รักโชค', 'กรุงไทย', 'xxx-x-x4291-x', 'demo');

// 21 REAL GLO tickets (barcodes decoded from the Data Matrix on each ticket photo).
// Columns: barcode(DataMatrix), alt_barcode(ITF), number, draw_date, draw_en, series, set,
//          price, status, is_claimed, prize_type, prize_amount
// Prize results for the 1 ก.ค. 2569 draw are a realistic DEMO set (see README) —
// the official results for that draw were not available, so winners were assigned to
// exercise every prize tier across the real tickets.
const tickets = [
  ['69-28-18-910054-3779','2628188702362700','910054','16 ก.ค. 2569','16 JULY 2026','28','18',80,'active',0,null,0],  // A (draw 16 ก.ค.)
  ['69-26-13-039184-4358','2626130402808908','039184','1 ก.ค. 2569','1 JULY 2026','26','13',80,'active',0,'รางวัลที่ 1',6000000],  // B
  ['69-26-37-488807-7121','2626371312530807','488807','1 ก.ค. 2569','1 JULY 2026','26','37',80,'active',0,'เลขท้าย 3 ตัว',4000],  // C
  ['69-25-05-972469-3941','2625058277231800','972469','1 ก.ค. 2569','1 JULY 2026','25','05',80,'active',0,'เลขหน้า 3 ตัว',4000],  // D
  ['69-25-04-972469-3941','','972469','1 ก.ค. 2569','1 JULY 2026','25','04',80,'active',0,'เลขหน้า 3 ตัว',4000],  // E
  ['69-25-03-972469-3941','2625039188568904','972469','1 ก.ค. 2569','1 JULY 2026','25','03',80,'active',0,'เลขหน้า 3 ตัว',4000],  // F
  ['69-25-02-972469-3941','2625028951310600','972469','1 ก.ค. 2569','1 JULY 2026','25','02',80,'active',0,'เลขหน้า 3 ตัว',4000],  // G
  ['69-25-01-972469-3941','','972469','1 ก.ค. 2569','1 JULY 2026','25','01',80,'active',0,'เลขหน้า 3 ตัว',4000],  // H
  ['69-25-03-127911-3943','2625033174570105','127911','1 ก.ค. 2569','1 JULY 2026','25','03',80,'active',0,'เลขหน้า 3 ตัว',4000],  // I
  ['69-25-05-127911-3943','','127911','1 ก.ค. 2569','1 JULY 2026','25','05',80,'active',0,'เลขหน้า 3 ตัว',4000],  // J
  ['69-25-04-127911-3943','','127911','1 ก.ค. 2569','1 JULY 2026','25','04',80,'active',0,'เลขหน้า 3 ตัว',4000],  // K
  ['69-25-02-127911-3943','2625028714370601','127911','1 ก.ค. 2569','1 JULY 2026','25','02',80,'active',0,'เลขหน้า 3 ตัว',4000],  // L
  ['69-25-01-127911-3943','','127911','1 ก.ค. 2569','1 JULY 2026','25','01',80,'active',0,'เลขหน้า 3 ตัว',4000],  // M
  ['69-26-12-965884-4359','2626120397183002','965884','1 ก.ค. 2569','1 JULY 2026','26','12',80,'active',0,null,0],  // N
  ['69-26-37-453545-1478','2626377603136304','453545','1 ก.ค. 2569','1 JULY 2026','26','37',80,'active',0,'เลขท้าย 3 ตัว',4000],  // O
  ['69-26-01-357788-0105','2626013734295003','357788','1 ก.ค. 2569','1 JULY 2026','26','01',100,'active',0,null,0],  // P (charity)
  ['69-26-38-453545-1478','2626385377053407','453545','1 ก.ค. 2569','1 JULY 2026','26','38',80,'active',0,'เลขท้าย 3 ตัว',4000],  // Q
  ['69-26-38-488807-7121','2626381252251504','488807','1 ก.ค. 2569','1 JULY 2026','26','38',80,'active',0,'เลขท้าย 3 ตัว',4000],  // R
  ['69-26-13-965884-4359','2626133850280207','965884','1 ก.ค. 2569','1 JULY 2026','26','13',80,'active',0,null,0],  // S
  ['69-26-32-568259-8004','2626325540539602','568259','1 ก.ค. 2569','1 JULY 2026','26','32',80,'active',0,'เลขท้าย 2 ตัว',2000],  // T
  ['69-26-31-568259-8004','2626315696356901','568259','1 ก.ค. 2569','1 JULY 2026','26','31',80,'active',0,'เลขท้าย 2 ตัว',2000]   // U
];

const stmt = db.prepare(`INSERT OR REPLACE INTO tickets
  (barcode,alt_barcode,number,draw_date,draw_en,series,"set",price,status,is_claimed,prize_type,prize_amount)
  VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`);
for (const t of tickets) stmt.run(...t);

console.log(`✅ Seeded ${tickets.length} real GLO tickets + 1 demo user into ${DB_PATH}`);
