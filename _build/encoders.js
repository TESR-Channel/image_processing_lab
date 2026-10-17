/* =============================================================================
 * TESR Image Processing Lab - encoders.js
 * -----------------------------------------------------------------------------
 * Dependency-free QR Code and EAN-13 encoders for the browser teaching tool.
 *
 * No imports, no npm packages, no build step. Drop this file in a <script> tag
 * (or load it in Node with require/import of the file path) and two globals
 * appear:
 *
 *   qrEncode(text, ecLevel)  ->  { version, ecLevel, mask, size, modules }
 *   ean13Encode(digits)      ->  { code, bits }
 *
 * Everything else lives inside the IIFE below, so nothing else can collide.
 * The few symbols that must be reachable for debugging are prefixed __qr / __ean.
 *
 * References: ISO/IEC 18004 (QR Code) and ISO/IEC 15420 (EAN/UPC).
 * ========================================================================== */

(function (global) {
  'use strict';

  /* ===========================================================================
   * SECTION 1 - QR CODE
   * ======================================================================== */

  /* ---------------------------------------------------------------------------
   * 1.1 Static tables from ISO/IEC 18004
   * ------------------------------------------------------------------------ */

  // Total number of codewords (data + error correction) for versions 1..20.
  // Index 0 is unused so that __qrTotalCodewords[v] reads naturally.
  var __qrTotalCodewords = [
    0,
    26, 44, 70, 100, 134, 172, 196, 242, 292, 346,
    404, 466, 532, 581, 655, 733, 815, 901, 991, 1085
  ];

  // Error correction characteristics (ISO/IEC 18004 Table 9).
  //
  // For each version 1..20 and each EC level we store:
  //   [ ecCodewordsPerBlock, blocksInGroup1, dataCodewordsPerBlockG1,
  //                          blocksInGroup2, dataCodewordsPerBlockG2 ]
  //
  // Group 2 is optional. When it exists its blocks always hold exactly one
  // more data codeword than group 1 blocks. The invariant that must hold is:
  //   ecPerBlock * (g1 + g2) + g1 * d1 + g2 * d2 === __qrTotalCodewords[v]
  var __qrEcTable = {
    L: [
      null,
      [7, 1, 19], [10, 1, 34], [15, 1, 55], [20, 1, 80], [26, 1, 108],
      [18, 2, 68], [20, 2, 78], [24, 2, 97], [30, 2, 116], [18, 2, 68, 2, 69],
      [20, 4, 81], [24, 2, 92, 2, 93], [26, 4, 107], [30, 3, 115, 1, 116],
      [22, 5, 87, 1, 88], [24, 5, 98, 1, 99], [28, 1, 107, 5, 108],
      [30, 5, 120, 1, 121], [28, 3, 113, 4, 114], [28, 3, 107, 5, 108]
    ],
    M: [
      null,
      [10, 1, 16], [16, 1, 28], [26, 1, 44], [18, 2, 32], [24, 2, 43],
      [16, 4, 27], [18, 4, 31], [22, 2, 38, 2, 39], [22, 3, 36, 2, 37],
      [26, 4, 43, 1, 44], [30, 1, 50, 4, 51], [22, 6, 36, 2, 37],
      [22, 8, 37, 1, 38], [24, 4, 40, 5, 41], [24, 5, 41, 5, 42],
      [28, 7, 45, 3, 46], [28, 10, 46, 1, 47], [26, 9, 43, 4, 44],
      [26, 3, 44, 11, 45], [26, 3, 41, 13, 42]
    ],
    Q: [
      null,
      [13, 1, 13], [22, 1, 22], [18, 2, 17], [26, 2, 24], [18, 2, 15, 2, 16],
      [24, 4, 19], [18, 2, 14, 4, 15], [22, 4, 18, 2, 19], [20, 4, 16, 4, 17],
      [24, 6, 19, 2, 20], [28, 4, 22, 4, 23], [26, 4, 20, 6, 21],
      [24, 8, 20, 4, 21], [20, 11, 16, 5, 17], [30, 5, 24, 7, 25],
      [24, 15, 19, 2, 20], [28, 1, 22, 15, 23], [28, 17, 22, 1, 23],
      [26, 17, 21, 4, 22], [30, 15, 24, 5, 25]
    ],
    H: [
      null,
      [17, 1, 9], [28, 1, 16], [22, 2, 13], [16, 4, 9], [22, 2, 11, 2, 12],
      [28, 4, 15], [26, 4, 13, 1, 14], [26, 4, 14, 2, 15], [24, 4, 12, 4, 13],
      [28, 6, 15, 2, 16], [24, 3, 12, 8, 13], [28, 7, 14, 4, 15],
      [22, 12, 11, 4, 12], [24, 11, 12, 5, 13], [24, 11, 12, 7, 13],
      [30, 3, 15, 13, 16], [28, 2, 14, 17, 15], [28, 2, 14, 19, 15],
      [26, 9, 13, 16, 14], [28, 15, 15, 10, 16]
    ]
  };

  // Row/column centres of the alignment patterns, versions 1..20.
  // Version 1 has none. Every combination of two centres gets a 5x5 pattern,
  // except the three combinations that would land on the finder patterns.
  var __qrAlignmentCentres = [
    null,
    [],
    [6, 18], [6, 22], [6, 26], [6, 30], [6, 34],
    [6, 22, 38], [6, 24, 42], [6, 26, 46], [6, 28, 50],
    [6, 30, 54], [6, 32, 58], [6, 34, 62],
    [6, 26, 46, 66], [6, 26, 48, 70], [6, 26, 50, 74], [6, 30, 54, 78],
    [6, 30, 56, 82], [6, 30, 58, 86], [6, 34, 62, 90]
  ];

  // 2-bit value written into the format information for each EC level.
  // Note this is NOT in L/M/Q/H order - that is simply what the spec says.
  var __qrEcFormatBits = { L: 1, M: 0, Q: 3, H: 2 };

  var __qrMaxVersion = 20;

  /* ---------------------------------------------------------------------------
   * 1.2 Galois field GF(256) arithmetic for Reed-Solomon
   * ------------------------------------------------------------------------ */

  // QR codes use GF(2^8) built on the primitive polynomial
  //   x^8 + x^4 + x^3 + x^2 + 1   (0x11D)
  // We precompute exponent and logarithm tables so that multiplication is
  // just "add the logs". This is the usual trick: a*b = exp[ log[a] + log[b] ].
  var __qrGfExp = new Uint8Array(512);
  var __qrGfLog = new Uint8Array(256);

  (function buildGaloisTables() {
    var x = 1;
    for (var i = 0; i < 255; i++) {
      __qrGfExp[i] = x;
      __qrGfLog[x] = i;
      // Multiply by the generator element 2, reducing modulo 0x11D when the
      // result overflows 8 bits.
      x <<= 1;
      if (x & 0x100) x ^= 0x11d;
    }
    // Duplicate the table so that index sums up to 510 need no modulo.
    for (var j = 255; j < 512; j++) __qrGfExp[j] = __qrGfExp[j - 255];
  }());

  function __qrGfMul(a, b) {
    if (a === 0 || b === 0) return 0;
    return __qrGfExp[__qrGfLog[a] + __qrGfLog[b]];
  }

  // Build the Reed-Solomon generator polynomial of the requested degree:
  //   g(x) = (x - a^0)(x - a^1) ... (x - a^(degree-1))
  // In GF(2^n) subtraction is XOR, so the signs do not matter.
  // Returned coefficients are in descending power order, with the implicit
  // leading 1 (for x^degree) omitted.
  function __qrRsGenerator(degree) {
    var result = [1];
    for (var i = 0; i < degree; i++) {
      var next = new Array(result.length + 1).fill(0);
      var factor = __qrGfExp[i]; // a^i
      for (var j = 0; j < result.length; j++) {
        next[j] ^= result[j];
        next[j + 1] ^= __qrGfMul(result[j], factor);
      }
      result = next;
    }
    return result; // length degree + 1, result[0] === 1
  }

  // Compute the `ecLen` error correction codewords for one block of data.
  // This is plain polynomial long division of data(x) * x^ecLen by the
  // generator polynomial; the remainder is the EC codeword sequence.
  function __qrRsRemainder(data, ecLen) {
    var gen = __qrRsGenerator(ecLen);
    var remainder = new Uint8Array(ecLen);
    for (var i = 0; i < data.length; i++) {
      var factor = data[i] ^ remainder[0];
      // Shift the remainder register left by one codeword.
      remainder.copyWithin(0, 1);
      remainder[ecLen - 1] = 0;
      if (factor !== 0) {
        for (var j = 0; j < ecLen; j++) {
          // gen[0] is the leading 1 we skip, so use gen[j + 1].
          remainder[j] ^= __qrGfMul(gen[j + 1], factor);
        }
      }
    }
    return remainder;
  }

  /* ---------------------------------------------------------------------------
   * 1.3 BCH codes for the format and version information
   * ------------------------------------------------------------------------ */

  // Generic BCH remainder: divide `value` (already shifted left by the number
  // of check bits) by `generator`, where `generator` has degree `checkBits`.
  function __qrBchRemainder(value, generator, checkBits) {
    var rem = value;
    var genBitLength = checkBits + 1;
    for (var i = genBitLength + checkBits - 1; i >= checkBits; i--) {
      if (rem & (1 << i)) rem ^= generator << (i - checkBits);
    }
    return rem & ((1 << checkBits) - 1);
  }

  // Format information: 5 data bits (2 for EC level, 3 for mask) protected by
  // a (15,5) BCH code with generator 0x537, then XORed with the fixed mask
  // 0x5412 so that an all-zero format never produces an all-light area.
  function __qrFormatBits(ecLevel, mask) {
    var data = (__qrEcFormatBits[ecLevel] << 3) | mask;       // 5 bits
    var rem = __qrBchRemainder(data << 10, 0x537, 10);
    return ((data << 10) | rem) ^ 0x5412;                      // 15 bits
  }

  // Version information (only present from version 7 up): 6 data bits
  // protected by an (18,6) BCH code with generator 0x1f25. No XOR mask.
  function __qrVersionBits(version) {
    var rem = __qrBchRemainder(version << 12, 0x1f25, 12);
    return (version << 12) | rem;                              // 18 bits
  }

  /* ---------------------------------------------------------------------------
   * 1.4 Helpers
   * ------------------------------------------------------------------------ */

  // Encode a JavaScript string as UTF-8 bytes.
  // QR byte mode carries raw bytes, so Thai (or any non-ASCII) text just works
  // as long as we hand it the UTF-8 encoding. TextEncoder exists in browsers
  // and in Node 11+, but we keep a manual fallback so the file stays portable.
  function __qrUtf8Bytes(text) {
    if (typeof TextEncoder === 'function') {
      return new TextEncoder().encode(String(text));
    }
    var str = String(text);
    var out = [];
    for (var i = 0; i < str.length; i++) {
      var cp = str.codePointAt(i);
      if (cp > 0xffff) i++; // surrogate pair consumed
      if (cp < 0x80) {
        out.push(cp);
      } else if (cp < 0x800) {
        out.push(0xc0 | (cp >> 6), 0x80 | (cp & 0x3f));
      } else if (cp < 0x10000) {
        out.push(0xe0 | (cp >> 12), 0x80 | ((cp >> 6) & 0x3f), 0x80 | (cp & 0x3f));
      } else {
        out.push(
          0xf0 | (cp >> 18),
          0x80 | ((cp >> 12) & 0x3f),
          0x80 | ((cp >> 6) & 0x3f),
          0x80 | (cp & 0x3f)
        );
      }
    }
    return new Uint8Array(out);
  }

  // Number of bits in the byte-mode character count indicator.
  function __qrCountBits(version) {
    return version <= 9 ? 8 : 16;
  }

  // Total data codewords available at a version / EC level combination.
  function __qrDataCodewords(version, ecLevel) {
    var spec = __qrEcTable[ecLevel][version];
    var total = spec[1] * spec[2];
    if (spec.length > 3) total += spec[3] * spec[4];
    return total;
  }

  /* ---------------------------------------------------------------------------
   * 1.5 Bit buffer
   * ------------------------------------------------------------------------ */

  function __qrBitBuffer() {
    this.bits = [];
  }
  __qrBitBuffer.prototype.push = function (value, length) {
    for (var i = length - 1; i >= 0; i--) {
      this.bits.push((value >>> i) & 1);
    }
  };
  __qrBitBuffer.prototype.pushByte = function (byte) {
    this.push(byte, 8);
  };
  __qrBitBuffer.prototype.toCodewords = function (count) {
    var out = new Uint8Array(count);
    for (var i = 0; i < this.bits.length; i++) {
      if (this.bits[i]) out[i >>> 3] |= 0x80 >>> (i & 7);
    }
    return out;
  };

  /* ---------------------------------------------------------------------------
   * 1.6 Data encoding: byte mode payload -> interleaved codeword stream
   * ------------------------------------------------------------------------ */

  function __qrBuildCodewords(bytes, version, ecLevel) {
    var dataCapacity = __qrDataCodewords(version, ecLevel);
    var buf = new __qrBitBuffer();

    buf.push(0x4, 4);                                 // mode indicator: byte mode
    buf.push(bytes.length, __qrCountBits(version));   // character count
    for (var i = 0; i < bytes.length; i++) buf.pushByte(bytes[i]);

    // Terminator: up to four zero bits, truncated if the capacity is reached.
    var capacityBits = dataCapacity * 8;
    var terminator = Math.min(4, capacityBits - buf.bits.length);
    buf.push(0, terminator);

    // Pad with zeros to the next byte boundary.
    while (buf.bits.length % 8 !== 0) buf.bits.push(0);

    // Then alternate the two fixed pad codewords 0xEC / 0x11 until full.
    var padToggle = true;
    while (buf.bits.length < capacityBits) {
      buf.pushByte(padToggle ? 0xec : 0x11);
      padToggle = !padToggle;
    }

    var dataCodewords = buf.toCodewords(dataCapacity);

    // Split into blocks, compute EC per block, then interleave.
    var spec = __qrEcTable[ecLevel][version];
    var ecPerBlock = spec[0];
    var groups = [[spec[1], spec[2]]];
    if (spec.length > 3) groups.push([spec[3], spec[4]]);

    var dataBlocks = [];
    var ecBlocks = [];
    var offset = 0;
    for (var g = 0; g < groups.length; g++) {
      for (var b = 0; b < groups[g][0]; b++) {
        var block = dataCodewords.subarray(offset, offset + groups[g][1]);
        offset += groups[g][1];
        dataBlocks.push(block);
        ecBlocks.push(__qrRsRemainder(block, ecPerBlock));
      }
    }

    // Interleaving: take codeword 0 of every block, then codeword 1 of every
    // block, and so on. Shorter blocks simply run out early and are skipped.
    var result = new Uint8Array(__qrTotalCodewords[version]);
    var pos = 0;
    var longestData = 0;
    for (var d = 0; d < dataBlocks.length; d++) {
      if (dataBlocks[d].length > longestData) longestData = dataBlocks[d].length;
    }
    for (var i2 = 0; i2 < longestData; i2++) {
      for (var j = 0; j < dataBlocks.length; j++) {
        if (i2 < dataBlocks[j].length) result[pos++] = dataBlocks[j][i2];
      }
    }
    for (var i3 = 0; i3 < ecPerBlock; i3++) {
      for (var k = 0; k < ecBlocks.length; k++) result[pos++] = ecBlocks[k][i3];
    }
    return result;
  }

  /* ---------------------------------------------------------------------------
   * 1.7 Matrix construction
   * ------------------------------------------------------------------------ */

  // A tiny matrix wrapper. Coordinates are (x = column, y = row).
  // `isFunction` marks modules that belong to a function pattern and therefore
  // must never carry data and must never be masked.
  function __qrMatrix(size) {
    this.size = size;
    this.modules = new Uint8Array(size * size);
    this.isFunction = new Uint8Array(size * size);
  }
  __qrMatrix.prototype.idx = function (x, y) {
    return y * this.size + x;
  };
  __qrMatrix.prototype.get = function (x, y) {
    return this.modules[y * this.size + x];
  };
  __qrMatrix.prototype.set = function (x, y, dark) {
    this.modules[y * this.size + x] = dark ? 1 : 0;
  };
  __qrMatrix.prototype.setFunction = function (x, y, dark) {
    this.modules[y * this.size + x] = dark ? 1 : 0;
    this.isFunction[y * this.size + x] = 1;
  };

  function __qrDrawFinder(m, cx, cy) {
    // A 9x9 region: concentric rings at Chebyshev distance 0..4 from the
    // centre. Distance 0,1,3 are dark; distance 2 and 4 (the separator) light.
    for (var dy = -4; dy <= 4; dy++) {
      for (var dx = -4; dx <= 4; dx++) {
        var x = cx + dx, y = cy + dy;
        if (x < 0 || y < 0 || x >= m.size || y >= m.size) continue;
        var dist = Math.max(Math.abs(dx), Math.abs(dy));
        m.setFunction(x, y, dist !== 2 && dist !== 4);
      }
    }
  }

  function __qrDrawAlignment(m, cx, cy) {
    // 5x5: dark centre, light ring, dark outer ring.
    for (var dy = -2; dy <= 2; dy++) {
      for (var dx = -2; dx <= 2; dx++) {
        m.setFunction(cx + dx, cy + dy, Math.max(Math.abs(dx), Math.abs(dy)) !== 1);
      }
    }
  }

  function __qrDrawFunctionPatterns(m, version, ecLevel) {
    var size = m.size;

    // Timing patterns: alternating dark/light along row 6 and column 6.
    for (var i = 0; i < size; i++) {
      m.setFunction(6, i, i % 2 === 0);
      m.setFunction(i, 6, i % 2 === 0);
    }

    // Three finder patterns with their separators.
    __qrDrawFinder(m, 3, 3);
    __qrDrawFinder(m, size - 4, 3);
    __qrDrawFinder(m, 3, size - 4);

    // Alignment patterns at every pair of centres, except the three pairs that
    // overlap the finder patterns (first/first, first/last, last/first).
    var centres = __qrAlignmentCentres[version];
    var n = centres.length;
    for (var a = 0; a < n; a++) {
      for (var b = 0; b < n; b++) {
        var skip = (a === 0 && b === 0) || (a === 0 && b === n - 1) || (a === n - 1 && b === 0);
        if (!skip) __qrDrawAlignment(m, centres[a], centres[b]);
      }
    }

    // Reserve the format information area with a placeholder (mask 0); the real
    // bits are written once the best mask is known.
    __qrDrawFormatInfo(m, ecLevel, 0);

    // Version information, two 3x6 blocks, only from version 7 up.
    if (version >= 7) {
      var vbits = __qrVersionBits(version);
      for (var k = 0; k < 18; k++) {
        var bit = (vbits >>> k) & 1;
        var p = size - 11 + (k % 3);
        var q = Math.floor(k / 3);
        m.setFunction(p, q, bit);   // block near the top-right finder
        m.setFunction(q, p, bit);   // block near the bottom-left finder
      }
    }
  }

  function __qrDrawFormatInfo(m, ecLevel, mask) {
    var bits = __qrFormatBits(ecLevel, mask);
    var size = m.size;
    var i;

    // First copy: an L shape hugging the top-left finder pattern.
    for (i = 0; i <= 5; i++) m.setFunction(8, i, (bits >>> i) & 1);
    m.setFunction(8, 7, (bits >>> 6) & 1);
    m.setFunction(8, 8, (bits >>> 7) & 1);
    m.setFunction(7, 8, (bits >>> 8) & 1);
    for (i = 9; i < 15; i++) m.setFunction(14 - i, 8, (bits >>> i) & 1);

    // Second copy: split between the bottom-left and top-right finders.
    for (i = 0; i < 8; i++) m.setFunction(size - 1 - i, 8, (bits >>> i) & 1);
    for (i = 8; i < 15; i++) m.setFunction(8, size - 15 + i, (bits >>> i) & 1);

    // The "dark module" - always 1, regardless of version or EC level.
    m.setFunction(8, size - 8, 1);
  }

  // Place the codeword bit stream into the matrix.
  // The path is two-module-wide columns walked from the right edge leftwards,
  // alternating upward and downward, skipping the vertical timing column 6.
  // Function modules are stepped over. Any modules left after the data runs
  // out stay light - these are the spec's "remainder bits", which are zero.
  function __qrPlaceCodewords(m, codewords) {
    var size = m.size;
    var bitIndex = 0;
    var totalBits = codewords.length * 8;

    for (var right = size - 1; right >= 1; right -= 2) {
      if (right === 6) right = 5; // the timing column is not part of the path
      for (var vert = 0; vert < size; vert++) {
        for (var j = 0; j < 2; j++) {
          var x = right - j;
          var upward = ((right + 1) & 2) === 0;
          var y = upward ? size - 1 - vert : vert;
          if (m.isFunction[m.idx(x, y)]) continue;
          if (bitIndex < totalBits) {
            var bit = (codewords[bitIndex >>> 3] >>> (7 - (bitIndex & 7))) & 1;
            m.set(x, y, bit);
            bitIndex++;
          }
        }
      }
    }
    return bitIndex;
  }

  /* ---------------------------------------------------------------------------
   * 1.8 Masking
   * ------------------------------------------------------------------------ */

  // The eight standard data mask conditions. Each returns true when the module
  // at (x = column, y = row) must be inverted.
  var __qrMaskFns = [
    function (x, y) { return (x + y) % 2 === 0; },
    function (x, y) { return y % 2 === 0; },
    function (x, y) { return x % 3 === 0; },
    function (x, y) { return (x + y) % 3 === 0; },
    function (x, y) { return (Math.floor(y / 2) + Math.floor(x / 3)) % 2 === 0; },
    function (x, y) { return ((x * y) % 2) + ((x * y) % 3) === 0; },
    function (x, y) { return (((x * y) % 2) + ((x * y) % 3)) % 2 === 0; },
    function (x, y) { return (((x + y) % 2) + ((x * y) % 3)) % 2 === 0; }
  ];

  // Apply (or, because XOR is its own inverse, un-apply) a mask to every
  // non-function module.
  function __qrApplyMask(m, mask) {
    var fn = __qrMaskFns[mask];
    for (var y = 0; y < m.size; y++) {
      for (var x = 0; x < m.size; x++) {
        var i = m.idx(x, y);
        if (m.isFunction[i]) continue;
        if (fn(x, y)) m.modules[i] ^= 1;
      }
    }
  }

  // The four penalty rules of ISO/IEC 18004 clause 7.8.3.1. Lower is better.
  //
  //   Rule 1  Runs of 5 or more same-coloured modules in a row or column:
  //           3 points for the first 5, +1 for every extra module.
  //   Rule 2  Every 2x2 block of one colour: 3 points.
  //   Rule 3  The 1:1:3:1:1 finder-like pattern (dark-light-dark*3-light-dark)
  //           with four light modules on either side: 40 points each.
  //   Rule 4  Deviation of the dark-module proportion from 50%:
  //           10 points for every full 5% away from half.
  function __qrPenalty(m) {
    var size = m.size;
    var score = 0;
    var x, y, run, runColour;

    // ---- Rule 1, horizontal and vertical runs -----------------------------
    for (y = 0; y < size; y++) {
      run = 1; runColour = m.get(0, y);
      for (x = 1; x < size; x++) {
        var c = m.get(x, y);
        if (c === runColour) {
          run++;
        } else {
          if (run >= 5) score += 3 + (run - 5);
          run = 1; runColour = c;
        }
      }
      if (run >= 5) score += 3 + (run - 5);
    }
    for (x = 0; x < size; x++) {
      run = 1; runColour = m.get(x, 0);
      for (y = 1; y < size; y++) {
        var c2 = m.get(x, y);
        if (c2 === runColour) {
          run++;
        } else {
          if (run >= 5) score += 3 + (run - 5);
          run = 1; runColour = c2;
        }
      }
      if (run >= 5) score += 3 + (run - 5);
    }

    // ---- Rule 2, 2x2 same-colour blocks -----------------------------------
    // Counting every 2x2 window gives the standard score: an NxM solid area
    // contributes 3*(N-1)*(M-1), which is exactly what the spec intends.
    for (y = 0; y < size - 1; y++) {
      for (x = 0; x < size - 1; x++) {
        var v = m.get(x, y);
        if (v === m.get(x + 1, y) && v === m.get(x, y + 1) && v === m.get(x + 1, y + 1)) {
          score += 3;
        }
      }
    }

    // ---- Rule 3, finder-like 1:1:3:1:1 patterns ---------------------------
    // Written out as the two literal 11-module sequences the spec describes:
    // the 1:1:3:1:1 core with the 4-module light margin before or after it.
    var patA = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0]; // core then light margin
    var patB = [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1]; // light margin then core
    function matchesAt(getter, start) {
      var a = true, b = true;
      for (var k = 0; k < 11; k++) {
        var val = getter(start + k);
        if (val !== patA[k]) a = false;
        if (val !== patB[k]) b = false;
        if (!a && !b) return 0;
      }
      return (a ? 1 : 0) + (b ? 1 : 0);
    }
    for (y = 0; y < size; y++) {
      var rowAt = (function (yy) {
        return function (xx) { return m.get(xx, yy); };
      }(y));
      for (x = 0; x + 11 <= size; x++) score += 40 * matchesAt(rowAt, x);
    }
    for (x = 0; x < size; x++) {
      var colAt = (function (xx) {
        return function (yy) { return m.get(xx, yy); };
      }(x));
      for (y = 0; y + 11 <= size; y++) score += 40 * matchesAt(colAt, y);
    }

    // ---- Rule 4, dark/light balance ---------------------------------------
    var dark = 0;
    for (var i = 0; i < m.modules.length; i++) dark += m.modules[i];
    var total = size * size;
    // How many whole 5% steps the dark proportion sits away from 50%.
    var steps = Math.floor(Math.abs(dark * 20 - total * 10) / total);
    score += steps * 10;

    return score;
  }

  /* ---------------------------------------------------------------------------
   * 1.9 Public QR entry point
   * ------------------------------------------------------------------------ */

  /**
   * Encode text as a QR Code symbol in byte mode.
   *
   * @param {string} text     Payload. Encoded as UTF-8 bytes, so Thai works.
   * @param {string} ecLevel  'L', 'M', 'Q' or 'H'.
   * @returns {{version:number, ecLevel:string, mask:number, size:number,
   *            modules:Uint8Array}}
   *          `modules` is row-major, length size*size, 1 = dark, 0 = light.
   *          No quiet zone is included.
   */
  function qrEncode(text, ecLevel) {
    if (text === undefined || text === null) {
      throw new Error('qrEncode: text is required');
    }
    var level = String(ecLevel === undefined ? 'M' : ecLevel).toUpperCase();
    if (!__qrEcTable[level]) {
      throw new Error('qrEncode: ecLevel must be one of L, M, Q, H (got "' + ecLevel + '")');
    }

    var bytes = __qrUtf8Bytes(text);

    // Pick the smallest version that can hold mode + count + payload.
    var version = -1;
    for (var v = 1; v <= __qrMaxVersion; v++) {
      var availableBits = __qrDataCodewords(v, level) * 8;
      var neededBits = 4 + __qrCountBits(v) + bytes.length * 8;
      if (neededBits <= availableBits) { version = v; break; }
    }
    if (version < 0) {
      var cap20 = Math.floor((__qrDataCodewords(__qrMaxVersion, level) * 8 - 4 - 16) / 8);
      throw new Error(
        'qrEncode: payload of ' + bytes.length + ' UTF-8 bytes does not fit in ' +
        'QR version ' + __qrMaxVersion + ' at EC level ' + level +
        ' (maximum ' + cap20 + ' bytes). Use a lower EC level or shorter text.'
      );
    }

    var size = version * 4 + 17;
    var codewords = __qrBuildCodewords(bytes, version, level);

    var m = new __qrMatrix(size);
    __qrDrawFunctionPatterns(m, version, level);
    __qrPlaceCodewords(m, codewords);

    // Try all eight masks, keep the one with the lowest penalty.
    // The format information depends on the mask, so it is rewritten each time
    // before scoring - its modules affect rules 1, 2 and 4.
    var bestMask = 0;
    var bestScore = Infinity;
    for (var mask = 0; mask < 8; mask++) {
      __qrDrawFormatInfo(m, level, mask);
      __qrApplyMask(m, mask);
      var score = __qrPenalty(m);
      __qrApplyMask(m, mask); // XOR again to undo
      if (score < bestScore) { bestScore = score; bestMask = mask; }
    }

    __qrDrawFormatInfo(m, level, bestMask);
    __qrApplyMask(m, bestMask);

    return {
      version: version,
      ecLevel: level,
      mask: bestMask,
      size: size,
      modules: m.modules
    };
  }

  /* ===========================================================================
   * SECTION 2 - EAN-13
   * ======================================================================== */

  /* ---------------------------------------------------------------------------
   * 2.1 The three symbol sets
   * ------------------------------------------------------------------------ */

  // EAN-13 encodes each digit as 7 modules. Three alphabets are used:
  //
  //   L (set A) - left half, odd parity  (an odd number of dark modules)
  //   G (set B) - left half, even parity (a mirror of R, read right-to-left)
  //   R (set C) - right half, even parity (the bitwise complement of L)
  //
  // Having two left-hand alphabets is what lets the 13th digit be carried
  // without any extra bars: the first digit is encoded purely in the *choice*
  // of L/G per position (see __eanParity below). It also makes the symbol
  // direction-detectable, since L starts with a light module and R with a dark.
  var __eanL = [
    '0001101', '0011001', '0010011', '0111101', '0100011',
    '0110001', '0101111', '0111011', '0110111', '0001011'
  ];
  var __eanG = [
    '0100111', '0110011', '0011011', '0100001', '0011101',
    '0111001', '0000101', '0010001', '0001001', '0010111'
  ];
  var __eanR = [
    '1110010', '1100110', '1101100', '1000010', '1011100',
    '1001110', '1010000', '1000100', '1001000', '1110100'
  ];

  // Which alphabet each of the six left-half digits uses, selected by the
  // leading (13th) digit. 'L' = set A, 'G' = set B.
  var __eanParity = [
    'LLLLLL', 'LLGLGG', 'LLGGLG', 'LLGGGL', 'LGLLGG',
    'LGGLLG', 'LGGGLL', 'LGLGLG', 'LGLGGL', 'LGGLGL'
  ];

  var __eanGuardStart = '101';
  var __eanGuardCentre = '01010';
  var __eanGuardEnd = '101';

  /* ---------------------------------------------------------------------------
   * 2.2 Check digit
   * ------------------------------------------------------------------------ */

  // Modulo-10 check digit: weight the first twelve digits 1,3,1,3,... from the
  // left, sum, and take whatever brings the total up to a multiple of ten.
  function __eanCheckDigit(first12) {
    var sum = 0;
    for (var i = 0; i < 12; i++) {
      var d = first12.charCodeAt(i) - 48;
      sum += (i % 2 === 0) ? d : d * 3;
    }
    return (10 - (sum % 10)) % 10;
  }

  /* ---------------------------------------------------------------------------
   * 2.3 Public EAN-13 entry point
   * ------------------------------------------------------------------------ */

  /**
   * Encode an EAN-13 barcode.
   *
   * @param {string} digits  12 digits (check digit is computed) or 13 digits
   *                         (check digit is verified).
   * @returns {{code:string, bits:string}}
   *          `code` is the full 13-digit number.
   *          `bits` is 95 characters of '0'/'1', left guard to right guard,
   *          where '1' = dark bar.
   */
  function ean13Encode(digits) {
    var s = String(digits === undefined || digits === null ? '' : digits).trim();

    if (!/^[0-9]+$/.test(s)) {
      throw new Error('ean13Encode: input must contain digits only (got "' + s + '")');
    }
    if (s.length !== 12 && s.length !== 13) {
      throw new Error(
        'ean13Encode: input must be 12 digits (check digit computed) or ' +
        '13 digits (check digit verified), got ' + s.length + ' digits'
      );
    }

    var code;
    if (s.length === 12) {
      code = s + String(__eanCheckDigit(s));
    } else {
      var expected = __eanCheckDigit(s.slice(0, 12));
      var given = s.charCodeAt(12) - 48;
      if (expected !== given) {
        throw new Error(
          'ean13Encode: check digit mismatch for "' + s + '" - expected ' +
          expected + ' but got ' + given
        );
      }
      code = s;
    }

    var lead = code.charCodeAt(0) - 48;
    var parity = __eanParity[lead];

    var bits = __eanGuardStart;
    // Left half: digits 2..7 of the code, alphabet chosen by the parity table.
    for (var i = 0; i < 6; i++) {
      var d = code.charCodeAt(1 + i) - 48;
      bits += (parity.charAt(i) === 'L') ? __eanL[d] : __eanG[d];
    }
    bits += __eanGuardCentre;
    // Right half: digits 8..13, always alphabet R.
    for (var j = 0; j < 6; j++) {
      bits += __eanR[code.charCodeAt(7 + j) - 48];
    }
    bits += __eanGuardEnd;

    // 3 + 6*7 + 5 + 6*7 + 3 = 95. Guard against a table typo.
    if (bits.length !== 95) {
      throw new Error('ean13Encode: internal error, produced ' + bits.length + ' bits');
    }

    return { code: code, bits: bits };
  }

  /* ===========================================================================
   * Exports - exactly two globals.
   * ======================================================================== */

  global.qrEncode = qrEncode;
  global.ean13Encode = ean13Encode;

}(typeof globalThis !== 'undefined' ? globalThis : this));
