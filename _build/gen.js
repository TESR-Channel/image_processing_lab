// Node harness: runs the encoders and dumps results as JSON for Python/OpenCV
// to decode. Run with:  node /home/claude/image_processing_lab/_build/gen.js
'use strict';

const fs = require('fs');
const path = require('path');

require(path.join(__dirname, 'encoders.js'));

const OUT = path.join(__dirname, 'cases.json');
const SWEEP_OUT = path.join(__dirname, 'sweep.json');

// ---------------------------------------------------------------------------
// Internal consistency check on the EC table before we trust any output.
// For every version/level: ecPerBlock*(blocks) + data codewords == total.
// We reach into the module by re-reading the file, since the tables live in a
// closure. Simpler: re-derive the invariant from a tiny eval of the table text.
// ---------------------------------------------------------------------------
function checkEcTable() {
  const src = fs.readFileSync(path.join(__dirname, 'encoders.js'), 'utf8');
  const totalMatch = src.match(/var __qrTotalCodewords = \[([\s\S]*?)\];/);
  const tableMatch = src.match(/var __qrEcTable = \{([\s\S]*?)\n  \};/);
  if (!totalMatch || !tableMatch) return ['could not locate tables for self-check'];
  // eslint-disable-next-line no-new-func
  const total = new Function('return [' + totalMatch[1] + '];')();
  // eslint-disable-next-line no-new-func
  const table = new Function('return {' + tableMatch[1] + '};')();
  const problems = [];
  for (const lvl of ['L', 'M', 'Q', 'H']) {
    for (let v = 1; v <= 20; v++) {
      const s = table[lvl][v];
      let n = s[0] * s[1] + s[1] * s[2];
      if (s.length > 3) n += s[0] * s[3] + s[3] * s[4];
      if (n !== total[v]) {
        problems.push(`v${v}-${lvl}: computed ${n}, table total ${total[v]}`);
      }
    }
  }
  return problems;
}

const ecProblems = checkEcTable();
if (ecProblems.length) {
  console.error('EC TABLE SELF-CHECK FAILED:');
  ecProblems.forEach((p) => console.error('  ' + p));
  process.exit(1);
}
console.log('EC table self-check: all 80 version/level combinations consistent.');

// ---------------------------------------------------------------------------
// QR cases
// ---------------------------------------------------------------------------
const ascii100 =
  'TESR Edge AI Vision Lab 0123456789 abcdefghijklmnopqrstuvwxyz ' +
  'ABCDEFGHIJKLMNOPQRSTUVWXYZ-=+*/.,;:!'; // trimmed/padded to exactly 100 below

const qrTexts = [
  { name: 'short-ascii', text: 'TESR' },
  { name: 'url', text: 'https://tesr-channel.github.io/image_processing_lab/' },
  { name: 'ascii-100', text: ascii100.slice(0, 100).padEnd(100, '.') },
  { name: 'thai-utf8', text: 'TESR ทดสอง ภาษาไทย' }
];

if (qrTexts[2].text.length !== 100) {
  throw new Error('ascii-100 case is ' + qrTexts[2].text.length + ' chars, expected 100');
}

const qrCases = [];
for (const t of qrTexts) {
  for (const lvl of ['L', 'M', 'Q', 'H']) {
    const r = qrEncode(t.text, lvl);
    qrCases.push({
      id: `${t.name}/${lvl}`,
      name: t.name,
      text: t.text,
      ecLevel: r.ecLevel,
      version: r.version,
      mask: r.mask,
      size: r.size,
      modules: Array.from(r.modules)
    });
  }
}

// Assert the mask actually varies - if penalty scoring were broken we would
// almost certainly see mask 0 everywhere.
const masksSeen = [...new Set(qrCases.map((c) => c.mask))].sort();
console.log('QR masks chosen across cases:', masksSeen.join(', '));
if (masksSeen.length < 2) {
  console.error('MASK VARIETY CHECK FAILED: every case picked the same mask.');
  process.exit(1);
}

// Throw-on-too-long check: version 20 at H holds far less than 2000 bytes.
let tooLongThrew = false;
let tooLongMessage = '';
try {
  qrEncode('x'.repeat(2000), 'H');
} catch (e) {
  tooLongThrew = true;
  tooLongMessage = e.message;
}

// Bad EC level check.
let badLevelThrew = false;
try {
  qrEncode('TESR', 'Z');
} catch (e) {
  badLevelThrew = true;
}

// ---------------------------------------------------------------------------
// EAN-13 cases
// ---------------------------------------------------------------------------
// The three required inputs, plus one code per leading digit 0-9. The leading
// digit selects which of the ten L/G parity patterns the left half uses, so
// without this sweep only 3 of the 10 parity rows would ever be exercised.
const eanInputs = ['590123412345', '000000000000', '123456789012'];
for (let d = 0; d <= 9; d++) {
  const candidate = String(d) + '01234567890';
  if (!eanInputs.includes(candidate)) eanInputs.push(candidate);
}
const eanCases = [];
for (const input of eanInputs) {
  const r = ean13Encode(input);
  eanCases.push({ id: input, input, code: r.code, bits: r.bits });
}

// One 13-digit input with the correct check digit (round-trip of case 1).
const good13 = eanCases[0].code;
const r13 = ean13Encode(good13);
eanCases.push({ id: good13 + ' (13-digit)', input: good13, code: r13.code, bits: r13.bits });
if (r13.bits !== eanCases[0].bits) {
  console.error('13-digit input produced different bits from the 12-digit form.');
  process.exit(1);
}

// One 13-digit input with a wrong check digit - must throw.
const bad13 = good13.slice(0, 12) + String((Number(good13[12]) + 1) % 10);
let badCheckThrew = false;
let badCheckMessage = '';
try {
  ean13Encode(bad13);
} catch (e) {
  badCheckThrew = true;
  badCheckMessage = e.message;
}

// Non-digit and wrong-length inputs - must throw.
const negatives = [];
for (const bad of ['59012341234A', '12345', '12345678901234', '']) {
  let threw = false;
  let msg = '';
  try { ean13Encode(bad); } catch (e) { threw = true; msg = e.message; }
  negatives.push({ input: bad, threw, message: msg });
}

// ---------------------------------------------------------------------------
fs.writeFileSync(
  OUT,
  JSON.stringify(
    {
      qr: qrCases,
      ean: eanCases,
      throwChecks: {
        qrTooLong: { threw: tooLongThrew, message: tooLongMessage },
        qrBadLevel: { threw: badLevelThrew },
        eanBadCheckDigit: { input: bad13, threw: badCheckThrew, message: badCheckMessage },
        eanNegatives: negatives
      }
    },
    null,
    1
  )
);

// ---------------------------------------------------------------------------
// Version sweep: one symbol per (version, EC level) pair, all 80 combinations.
// The four named cases above only touch 8 of the 80 rows of the EC block table,
// so this sweep is what actually exercises every row. Payloads grow one byte
// at a time and we keep the first payload that lands on each version.
// Consumed by crosscheck.py.
// ---------------------------------------------------------------------------
const sweep = [];
for (const lvl of ['L', 'M', 'Q', 'H']) {
  const seen = new Set();
  for (let n = 1; n <= 2000; n++) {
    let r;
    try {
      r = qrEncode('A'.repeat(n), lvl);
    } catch (e) {
      break; // past the version 20 capacity for this level
    }
    if (!seen.has(r.version)) {
      seen.add(r.version);
      sweep.push({
        id: `v${r.version}-${lvl}`,
        text: 'A'.repeat(n),
        ecLevel: r.ecLevel,
        version: r.version,
        mask: r.mask,
        size: r.size,
        modules: Array.from(r.modules)
      });
    }
  }
}
if (sweep.length !== 80) {
  console.error(`SWEEP FAILED: expected 80 version/level combinations, got ${sweep.length}`);
  process.exit(1);
}
fs.writeFileSync(SWEEP_OUT, JSON.stringify({ qr: sweep }));
console.log(`Wrote sweep of ${sweep.length} version/level combinations to ${SWEEP_OUT}`);

console.log(`Wrote ${qrCases.length} QR cases and ${eanCases.length} EAN cases to ${OUT}`);
console.log('QR version/mask summary:');
for (const c of qrCases) {
  console.log(`  ${c.id.padEnd(18)} v${String(c.version).padStart(2)}  mask ${c.mask}  size ${c.size}`);
}
console.log('Throw checks:', JSON.stringify({
  qrTooLong: tooLongThrew,
  qrBadLevel: badLevelThrew,
  eanBadCheckDigit: badCheckThrew,
  eanNegatives: negatives.map((n) => n.threw)
}));
