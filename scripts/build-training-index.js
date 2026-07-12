const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const realTicketsPath = path.join(root, 'data', 'real-tickets.json');
const realImagesDir = path.join(root, 'data', 'ticket-images');
const manualDir = path.join(root, 'data', 'manual-dimension-test');
const fakeLabelsPath = path.join(manualDir, 'labels.csv');
const outDir = path.join(root, 'data', 'training-dataset');

function exists(file) {
  return fs.existsSync(file);
}

function parseCsvLine(line) {
  const values = [];
  let current = '';
  let quoted = false;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if (ch === '"') {
      if (quoted && line[i + 1] === '"') {
        current += '"';
        i += 1;
      } else {
        quoted = !quoted;
      }
    } else if (ch === ',' && !quoted) {
      values.push(current);
      current = '';
    } else {
      current += ch;
    }
  }
  values.push(current);
  return values;
}

function readCsv(file) {
  const rows = fs.readFileSync(file, 'utf8').trim().split(/\r?\n/);
  const headers = parseCsvLine(rows.shift());
  return rows.filter(Boolean).map((line) => {
    const values = parseCsvLine(line);
    return Object.fromEntries(headers.map((key, index) => [key, values[index] || '']));
  });
}

function csvEscape(value) {
  const text = String(value ?? '');
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function main() {
  const samples = [];
  const realTickets = JSON.parse(fs.readFileSync(realTicketsPath, 'utf8'));

  for (const ticket of realTickets) {
    const relativePath = `data/ticket-images/${ticket.folder}.jpg`;
    const absolutePath = path.join(root, relativePath);
    samples.push({
      sample_id: `REAL_${ticket.folder}`,
      relative_path: relativePath,
      class_label: 'genuine',
      is_fake: false,
      dimension: 'none',
      region: 'full_ticket',
      severity: 'none',
      barcode: ticket.barcode,
      number: ticket.number,
      exists: exists(absolutePath)
    });
  }

  if (exists(fakeLabelsPath)) {
    for (const row of readCsv(fakeLabelsPath)) {
      const relativePath = `data/manual-dimension-test/${row.relative_path}`;
      const absolutePath = path.join(root, relativePath);
      samples.push({
        sample_id: row.sample_id,
        relative_path: relativePath,
        class_label: 'fake',
        is_fake: true,
        dimension: row.dimension,
        region: row.region,
        severity: row.severity,
        barcode: '',
        number: '',
        exists: exists(absolutePath),
        notes: row.notes || ''
      });
    }
  }

  const summary = samples.reduce((acc, sample) => {
    acc.total += 1;
    acc.existing += sample.exists ? 1 : 0;
    acc.missing += sample.exists ? 0 : 1;
    acc.by_class[sample.class_label] = (acc.by_class[sample.class_label] || 0) + 1;
    acc.by_dimension[sample.dimension] = (acc.by_dimension[sample.dimension] || 0) + 1;
    return acc;
  }, { total: 0, existing: 0, missing: 0, by_class: {}, by_dimension: {} });

  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, 'index.json'), JSON.stringify({
    generated_at: new Date().toISOString(),
    purpose: 'genuine_vs_fake_image_training',
    summary,
    samples
  }, null, 2));

  const headers = ['sample_id', 'relative_path', 'class_label', 'is_fake', 'dimension', 'region', 'severity', 'exists', 'barcode', 'number', 'notes'];
  const csv = [headers.join(',')]
    .concat(samples.map((sample) => headers.map((key) => csvEscape(sample[key])).join(',')))
    .join('\n') + '\n';
  fs.writeFileSync(path.join(outDir, 'labels.csv'), csv);

  console.log(`Wrote ${samples.length} samples to ${path.relative(root, outDir)}`);
  console.log(`Existing files: ${summary.existing}; missing files: ${summary.missing}`);
}

main();
