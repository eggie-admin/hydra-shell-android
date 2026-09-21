#!/usr/bin/env node
// LUHM_COMPILE_WIZARD_V1

import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import readline from 'node:readline/promises';
import process from 'node:process';

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
export const GAME = join(ROOT, 'project/hydra/samsung/android/cathedral-game');
export const WORKFLOW = 'luhmos-drive-avatar-candidate.yml';
export const CANDIDATE_PACKAGE = 'art.eggiebagelface.luhmos.candidate';
export const RELEASE_PACKAGE = 'art.eggiebagelface.luhmos';
export const APK_BASENAME = 'luhmos-lum-avatar-candidate-1.0.10.apk';

export const COMMANDS = Object.freeze([
  'start',
  'options',
  'test',
  'dryrun',
  'audit',
  'build',
  'install',
]);

const argv = process.argv.slice(2);

function banner() {
  console.log('\n⚡ LuHm OS Universal Remote Forge Wizard ⚡');
  console.log('   test first, dry-run second, candidate build third, Crown-gated install last\n');
}

function commandResult(command, args = [], options = {}) {
  const result = spawnSync(command, args, {
    cwd: options.cwd ?? ROOT,
    env: { ...process.env, ...(options.env ?? {}) },
    encoding: 'utf8',
    stdio: options.capture ? ['ignore', 'pipe', 'pipe'] : 'inherit',
    shell: false,
  });
  if (result.error) {
    return { status: 127, stdout: '', stderr: result.error.message };
  }
  return {
    status: result.status ?? 1,
    stdout: result.stdout ?? '',
    stderr: result.stderr ?? '',
  };
}

function run(command, args = [], options = {}) {
  console.log(`⚙ ${command} ${args.join(' ')}`.trim());
  const result = commandResult(command, args, options);
  if (result.status !== 0) {
    const detail = options.capture ? `\n${result.stdout}${result.stderr}` : '';
    throw new Error(`${command} failed with exit ${result.status}${detail}`);
  }
  return result;
}

function capture(command, args = [], options = {}) {
  return run(command, args, { ...options, capture: true }).stdout.trim();
}

function toolExists(command, args = ['--version']) {
  return commandResult(command, args, { capture: true }).status === 0;
}

function sha256(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex');
}

function findFiles(root, predicate, result = []) {
  if (!existsSync(root)) return result;
  for (const name of readdirSync(root)) {
    const path = join(root, name);
    const st = statSync(path);
    if (st.isDirectory()) findFiles(path, predicate, result);
    else if (predicate(path)) result.push(path);
  }
  return result;
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function packageJson() {
  return JSON.parse(readFileSync(join(ROOT, 'package.json'), 'utf8'));
}

function packageLock() {
  return JSON.parse(readFileSync(join(ROOT, 'package-lock.json'), 'utf8'));
}

export function requestedApply(args) {
  return args.includes('--apply');
}

export function lifecycleInstallNoop(env = process.env, args = []) {
  return env.npm_command === 'install' && !requestedApply(args) && !args.includes('--apk');
}

export function makeDryRunPlan(sourceSha = 'local') {
  return {
    schema: 'luhm_os.npm_compile_wizard_plan.v1',
    source_sha: sourceSha,
    sequence: ['test', 'dryrun', 'build', 'install'],
    build: {
      workflow: WORKFLOW,
      artifact: APK_BASENAME,
      package: CANDIDATE_PACKAGE,
      production_package: RELEASE_PACKAGE,
      release_signing: false,
      deploy: false,
    },
    install: {
      default: 'staged_only',
      explicit_apply_flag: '--apply',
      exactly_one_adb_device_required: true,
      accepted_package: CANDIDATE_PACKAGE,
    },
    authority: {
      canonical_merge: 'NOT_TRIGGERED',
      production_deploy: 'NOT_TRIGGERED',
      release_signing: 'NOT_TRIGGERED',
      crown: 'NOT_TRIGGERED',
    },
  };
}

export function isCandidatePackage(packageId) {
  return packageId === CANDIDATE_PACKAGE;
}

function getSourceSha() {
  const result = commandResult('git', ['rev-parse', 'HEAD'], { capture: true });
  return result.status === 0 ? result.stdout.trim() : 'local';
}

function getBranch() {
  if (process.env.GITHUB_HEAD_REF) return process.env.GITHUB_HEAD_REF;
  const result = commandResult('git', ['branch', '--show-current'], { capture: true });
  return result.status === 0 ? result.stdout.trim() : '';
}

function checkNodeAndNpm() {
  const nodeMajor = Number(process.versions.node.split('.')[0]);
  assert(nodeMajor === 24, `Node 24 required, observed ${process.versions.node}`);
  const npmVersion = capture('npm', ['--version']);
  const npmMajor = Number(npmVersion.split('.')[0]);
  assert(npmMajor === 11, `npm 11 required, observed ${npmVersion}`);
}

function scanSecrets(paths) {
  const patterns = [
    /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/,
    /\bsk-[A-Za-z0-9_-]{20,}\b/,
    /\bAIza[A-Za-z0-9_-]{20,}\b/,
    /\bBearer\s+[A-Za-z0-9._-]{20,}\b/i,
  ];
  for (const path of paths) {
    const text = readFileSync(path, 'utf8');
    for (const pattern of patterns) {
      assert(!pattern.test(text), `secret-like material detected in ${path}`);
    }
  }
}

export function audit() {
  banner();
  console.log('🔍 hard audit');
  checkNodeAndNpm();

  const pkg = packageJson();
  const lock = packageLock();
  assert(pkg.private === true, 'package must stay private');
  assert(pkg.version === '1.0.10', 'wizard package version drift');
  for (const key of COMMANDS) assert(typeof pkg.scripts?.[key] === 'string', `missing npm script: ${key}`);
  assert(lock.lockfileVersion === 3, 'package-lock must use lockfileVersion 3');
  assert(Object.keys(lock.packages ?? {}).length === 1 && lock.packages[''], 'root package-lock must remain zero-dependency');
  assert(!pkg.dependencies && !pkg.devDependencies, 'compile wizard must remain zero-dependency');

  run('git', ['diff', '--check']);
  run('python3', [join(GAME, 'tools/validate-forge.py'), GAME]);
  run('python3', [join(GAME, 'tools/validate-source.py'), GAME]);
  run('python3', ['-m', 'compileall', '-q', join(GAME, 'tools'), join(GAME, 'python/src')]);
  run('node', ['--check', join(ROOT, 'tools/luhm-compile-wizard.mjs')]);
  run('node', ['--test', join(ROOT, 'tools/luhm-compile-wizard.test.mjs')]);
  run('node', ['--check', join(GAME, 'apk-install-gui.js')]);
  run('node', ['--test', join(GAME, 'tests/apk-install-gui.test.mjs')]);

  scanSecrets([
    join(ROOT, 'package.json'),
    join(ROOT, 'package-lock.json'),
    join(ROOT, 'tools/luhm-compile-wizard.mjs'),
    join(ROOT, '.github/workflows/luhmos-universal-forge-gate.yml'),
    join(ROOT, '.github/workflows/luhmos-drive-avatar-candidate.yml'),
  ]);

  console.log('✅ LUHM_COMPILE_WIZARD_AUDIT_GREEN');
  return 0;
}

export function test() {
  audit();
  const plan = makeDryRunPlan(getSourceSha());
  assert(plan.sequence.join('>') === 'test>dryrun>build>install', 'wizard sequence drift');
  assert(plan.build.package === CANDIDATE_PACKAGE, 'candidate package drift');
  assert(plan.install.default === 'staged_only', 'install default must remain staged');
  console.log('✅ LUHM_COMPILE_WIZARD_TEST_GREEN');
  return 0;
}

export function dryrun() {
  audit();
  const plan = makeDryRunPlan(getSourceSha());
  console.log('\n🧪 DRY RUN ONLY. No build dispatched. No APK installed.');
  console.log(JSON.stringify(plan, null, 2));
  console.log('✅ LUHM_COMPILE_WIZARD_DRYRUN_GREEN');
  return 0;
}

function options() {
  banner();
  console.log('1) options   show this menu');
  console.log('2) test      hard audit + tests');
  console.log('3) dryrun    prove the plan without mutation');
  console.log('4) build     dispatch pinned remote candidate forge, wait, download proof');
  console.log('5) install   verify candidate APK; stage only unless --apply is explicit');
  console.log('6) start     interactive wizard');
  console.log('\nSuggested flow: npm test && npm run dryrun && npm run build && npm run install');
  console.log('Apply install only when intended: npm run install -- --apply');
  return 0;
}

function ghLatestRunForSource(sourceSha, branch) {
  for (let attempt = 0; attempt < 30; attempt += 1) {
    const result = commandResult('gh', [
      'run', 'list',
      '--workflow', WORKFLOW,
      '--branch', branch,
      '--event', 'workflow_dispatch',
      '--limit', '10',
      '--json', 'databaseId,headSha,status,conclusion,createdAt',
    ], { capture: true });
    if (result.status === 0) {
      const rows = JSON.parse(result.stdout || '[]');
      const match = rows.find((row) => row.headSha === sourceSha);
      if (match) return match.databaseId;
    }
    commandResult('sleep', ['2'], { capture: true });
  }
  throw new Error('remote workflow run did not appear for the current source SHA');
}

function build() {
  audit();
  assert(toolExists('gh', ['--version']), 'GitHub CLI `gh` is required for automated remote candidate build');
  run('gh', ['auth', 'status']);
  const branch = getBranch();
  assert(/^luhmos\//.test(branch), `refusing remote build from unexpected branch: ${branch || '<detached>'}`);
  const sourceSha = getSourceSha();

  console.log(`🚀 dispatching ${WORKFLOW} for ${branch}`);
  run('gh', ['workflow', 'run', WORKFLOW, '--ref', branch]);
  const runId = ghLatestRunForSource(sourceSha, branch);
  console.log(`🛰 remote run ${runId}`);
  run('gh', ['run', 'watch', String(runId), '--exit-status', '--interval', '5']);

  const outDir = join(ROOT, 'build', `remote-run-${runId}`);
  mkdirSync(outDir, { recursive: true });
  run('gh', ['run', 'download', String(runId), '-D', outDir]);
  const apks = findFiles(outDir, (path) => basename(path) === APK_BASENAME);
  assert(apks.length === 1, `expected exactly one ${APK_BASENAME}, found ${apks.length}`);

  const receipt = {
    schema: 'luhm_os.npm_compile_wizard_build_receipt.v1',
    source_sha: sourceSha,
    branch,
    workflow: WORKFLOW,
    run_id: runId,
    apk: apks[0].slice(ROOT.length + 1),
    apk_sha256: sha256(apks[0]),
    package: CANDIDATE_PACKAGE,
    production_signing: false,
    deploy: false,
    crown: 'NOT_TRIGGERED',
  };
  mkdirSync(join(ROOT, 'build'), { recursive: true });
  writeFileSync(join(ROOT, 'build', 'LUHM_WIZARD_BUILD_RECEIPT.json'), `${JSON.stringify(receipt, null, 2)}\n`);
  console.log(JSON.stringify(receipt, null, 2));
  console.log('✅ LUHM_COMPILE_WIZARD_BUILD_GREEN');
  return 0;
}

function locateAapt() {
  if (toolExists('aapt', ['version'])) return 'aapt';
  const sdk = process.env.ANDROID_HOME || process.env.ANDROID_SDK_ROOT;
  if (!sdk) return null;
  const root = join(sdk, 'build-tools');
  if (!existsSync(root)) return null;
  const versions = readdirSync(root).sort().reverse();
  for (const version of versions) {
    const path = join(root, version, process.platform === 'win32' ? 'aapt.exe' : 'aapt');
    if (existsSync(path)) return path;
  }
  return null;
}

function parseApkArg(args) {
  const index = args.indexOf('--apk');
  return index >= 0 ? args[index + 1] : null;
}

function latestCandidateApk() {
  const matches = findFiles(join(ROOT, 'build'), (path) => basename(path) === APK_BASENAME);
  if (!matches.length) return null;
  return matches.sort((a, b) => statSync(b).mtimeMs - statSync(a).mtimeMs)[0];
}

function verifyCandidateApk(apk) {
  assert(apk && existsSync(apk), `candidate APK not found: ${apk ?? '<none>'}`);
  const aapt = locateAapt();
  let badging = '';
  if (aapt) {
    badging = capture(aapt, ['dump', 'badging', apk]);
  } else {
    const nearby = findFiles(dirname(apk), (path) => basename(path) === 'badging.txt');
    assert(nearby.length > 0, 'aapt unavailable and no badging.txt proof found beside artifact');
    badging = readFileSync(nearby[0], 'utf8');
  }
  const match = badging.match(/package:\s+name='([^']+)'/);
  assert(match, 'APK package id could not be proven');
  assert(isCandidatePackage(match[1]), `refusing non-candidate package: ${match[1]}`);
  assert(match[1] !== RELEASE_PACKAGE, 'production package must never be installed by wizard');
  return { packageId: match[1], sha256: sha256(apk) };
}

function install(args) {
  if (lifecycleInstallNoop(process.env, args)) {
    console.log('🛡 npm install lifecycle detected: LuHm device install is a safe no-op.');
    console.log('Use `npm run install` to stage a candidate or `npm run install -- --apply` to explicitly apply.');
    return 0;
  }

  audit();
  const explicit = parseApkArg(args);
  const apk = explicit ? resolve(ROOT, explicit) : latestCandidateApk();
  const proof = verifyCandidateApk(apk);
  console.log(`🔏 candidate ${proof.packageId}`);
  console.log(`🔏 sha256 ${proof.sha256}`);

  if (!requestedApply(args)) {
    console.log('🧷 INSTALL_STAGED_CROWN_REQUIRED');
    console.log(`No device mutation performed. Apply explicitly with: npm run install -- --apply --apk ${apk}`);
    return 0;
  }

  assert(toolExists('adb', ['version']), 'adb is required for explicit device install');
  const devices = capture('adb', ['devices'])
    .split(/\r?\n/)
    .slice(1)
    .map((line) => line.trim())
    .filter(Boolean)
    .filter((line) => /\tdevice$/.test(line));
  assert(devices.length === 1, `explicit install requires exactly one authorized adb device; found ${devices.length}`);
  run('adb', ['install', '-r', apk]);
  console.log('✅ LUHM_COMPILE_WIZARD_INSTALL_APPLIED');
  return 0;
}

async function start() {
  banner();
  if (!process.stdin.isTTY || !process.stdout.isTTY) {
    console.log('Non-interactive shell detected. Showing safe options only.');
    return options();
  }
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  try {
    while (true) {
      console.log('1 test  |  2 dryrun  |  3 build  |  4 install  |  5 build -> install  |  0 exit');
      const answer = (await rl.question('LuHm forge> ')).trim();
      if (answer === '0') return 0;
      if (answer === '1') test();
      else if (answer === '2') dryrun();
      else if (answer === '3') build();
      else if (answer === '4') install([]);
      else if (answer === '5') {
        build();
        const apply = (await rl.question('Type APPLY to install the verified candidate on exactly one adb device, or press Enter to stage only: ')).trim();
        install(apply === 'APPLY' ? ['--apply'] : []);
      } else options();
    }
  } finally {
    rl.close();
  }
}

async function main() {
  const command = argv[0] ?? 'start';
  const args = argv.slice(1);
  assert(COMMANDS.includes(command), `unknown command: ${command}`);
  if (command === 'start') return start();
  if (command === 'options') return options();
  if (command === 'test') return test();
  if (command === 'dryrun') return dryrun();
  if (command === 'audit') return audit();
  if (command === 'build') return build();
  if (command === 'install') return install(args);
  return 2;
}

const invokedDirectly = process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href;
if (invokedDirectly) {
  main().then((code) => process.exit(code ?? 0)).catch((error) => {
    console.error(`❌ LUHM_COMPILE_WIZARD_RED: ${error.message}`);
    process.exit(2);
  });
}
