#!/usr/bin/env node
// Mr. One: Mr. P's brain (research/pm15_copilot.html) with Mr. E's hands — one resting limit order at a time, re-priced every
// second from the settlement index; never a taker fill on entry. This is scripts/pm15_live.js in --maker mode; see its header.
//   node scripts/mr1_live.js research/pm15_copilot.html [--dry] [--replay btc15_windows.json --strict 1] [--cross]
'use strict';
process.env.MRP_POLICY = 'maker'; process.env.MRP_NAME = process.env.MRP_NAME || 'Mr. One';
if (!process.argv.includes('--maker')) process.argv.push('--maker');
require('./pm15_live.js');
