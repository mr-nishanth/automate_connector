# Automate Connector

## Overview

The `automate-connector` repository contains the vendor-specific integration responsible for extracting dealership data from the Automate DMS and preparing it for migration into Tekion ARC.

This connector owns its Automate-specific authentication, navigation, extraction workflows, data handling, transformation and migration behaviour.

It is maintained independently from the other DMS connectors because Automate has its own interface, extraction sequence and data structures.

## Responsibilities

- Connect to the authorized Automate DMS environment.
- Authenticate using the existing supported authentication mechanism.
- Navigate Automate-specific workflows.
- Extract supported dealership data.
- Handle vendor-specific extraction failures.
- Transform extracted data into the required ARC-compatible format.
- Preserve existing migration behaviour and data integrity.
- Report extraction and processing errors.

## Vendor Identity

| Property | Value |
|---|---|
| Vendor | AUTOMATE |
| Repository | automate-connector |
| Target platform | Tekion ARC |
| Connector type | Vendor-specific DMS connector |

## Architecture

The connector must maintain its own implementation of the vendor-specific extraction workflow.

Document the actual implementation here:

- Authentication mechanism: To be documented
- Navigation mechanism: To be documented
- Extraction workflow: To be documented
- Supported data entities: To be documented
- Transformation and mapping: To be documented
- Error-handling strategy: To be documented

## Vendor-Specific Workflow

Document the actual Automate extraction sequence here.

| Workflow | Extraction steps | Status |
|---|---|---|
| Customer data | To be documented | Pending |
| Vehicle data | To be documented | Pending |
| Deal data | To be documented | Pending |
| Service data | To be documented | Pending |

Do not assume that Automate workflow steps correspond to steps in another vendor connector.

## Repository Development Guidelines

1. Preserve existing extraction behaviour unless the requested change requires modifying it.
2. Avoid unrelated refactoring.
3. Maintain existing naming and architectural conventions.
4. Preserve backward compatibility where required.
5. Add or update tests for every affected behaviour.
6. Do not introduce changes to other vendor connectors.

## AI Migration Agent Integration

This repository is registered under the logical vendor identifier `AUTOMATE`.

When a Jira Story identifies `AUTOMATE`, the central repository registry must resolve it to this repository.

The AI Migration Agent may:

- Analyze relevant source files.
- Investigate Automate-specific workflow failures.
- Identify affected functions and dependencies.
- Prepare a targeted implementation plan.
- Modify relevant code in an isolated workspace.
- Run available deterministic tests.
- Produce a Git diff for validation.

The AI agent must not select another vendor repository or expand its scope beyond this connector.

## Testing and Validation

Before creating a pull request:

- Run relevant unit tests.
- Run relevant integration tests where available.
- Run existing lint and type-check commands where configured.
- Inspect the complete Git diff.
- Check for unrelated modifications.
- Verify that existing connector behaviour has not been unintentionally changed.

Actual commands must be documented after repository inspection.

## Security

- Never commit credentials, passwords, cookies or API tokens.
- Do not include dealership credentials in logs or Jira comments.
- Use approved secure credential handling.
- Preserve existing authorization and data-protection controls.

## Documentation Maintenance

Update this README when the actual extraction architecture, supported workflows, development commands or testing requirements change.

**Note:** This README documents the intended repository responsibilities. Actual implementation details must be verified against the source code.
