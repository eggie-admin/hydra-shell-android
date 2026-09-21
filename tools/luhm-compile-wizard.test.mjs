import assert from 'node:assert/strict';
import test from 'node:test';

import {
  CANDIDATE_PACKAGE,
  COMMANDS,
  RELEASE_PACKAGE,
  isCandidatePackage,
  lifecycleInstallNoop,
  makeDryRunPlan,
  requestedApply,
} from './luhm-compile-wizard.mjs';

test('wizard exposes required command surface', () => {
  for (const command of ['start', 'options', 'test', 'dryrun', 'build', 'install']) {
    assert.equal(COMMANDS.includes(command), true);
  }
});

test('dry-run plan stays candidate-only and Crown-gated', () => {
  const plan = makeDryRunPlan('abc123');
  assert.equal(plan.source_sha, 'abc123');
  assert.deepEqual(plan.sequence, ['test', 'dryrun', 'build', 'install']);
  assert.equal(plan.build.package, CANDIDATE_PACKAGE);
  assert.equal(plan.build.production_package, RELEASE_PACKAGE);
  assert.equal(plan.build.release_signing, false);
  assert.equal(plan.build.deploy, false);
  assert.equal(plan.install.default, 'staged_only');
  assert.equal(plan.authority.crown, 'NOT_TRIGGERED');
});

test('ordinary npm install lifecycle cannot mutate a device', () => {
  assert.equal(lifecycleInstallNoop({ npm_command: 'install' }, []), true);
  assert.equal(lifecycleInstallNoop({ npm_command: 'run-script' }, []), false);
});

test('device mutation requires explicit apply flag', () => {
  assert.equal(requestedApply([]), false);
  assert.equal(requestedApply(['--apply']), true);
});

test('wizard accepts only the collision-free candidate package', () => {
  assert.equal(isCandidatePackage(CANDIDATE_PACKAGE), true);
  assert.equal(isCandidatePackage(RELEASE_PACKAGE), false);
  assert.equal(isCandidatePackage('com.example.other'), false);
});
