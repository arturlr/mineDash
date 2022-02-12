/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const createLoginAudit = /* GraphQL */ `
  mutation CreateLoginAudit(
    $input: CreateLoginAuditInput!
    $condition: ModelLoginAuditConditionInput
  ) {
    createLoginAudit(input: $input, condition: $condition) {
      id
      email
      action
      expirationEpoch
      createdAt
      updatedAt
    }
  }
`;
export const updateLoginAudit = /* GraphQL */ `
  mutation UpdateLoginAudit(
    $input: UpdateLoginAuditInput!
    $condition: ModelLoginAuditConditionInput
  ) {
    updateLoginAudit(input: $input, condition: $condition) {
      id
      email
      action
      expirationEpoch
      createdAt
      updatedAt
    }
  }
`;
export const deleteLoginAudit = /* GraphQL */ `
  mutation DeleteLoginAudit(
    $input: DeleteLoginAuditInput!
    $condition: ModelLoginAuditConditionInput
  ) {
    deleteLoginAudit(input: $input, condition: $condition) {
      id
      email
      action
      expirationEpoch
      createdAt
      updatedAt
    }
  }
`;
export const createEc2Events = /* GraphQL */ `
  mutation CreateEc2Events(
    $input: CreateEc2EventsInput!
    $condition: ModelEc2EventsConditionInput
  ) {
    createEc2Events(input: $input, condition: $condition) {
      id
      instanceId
      json
      expirationEpoch
      createdAt
      updatedAt
    }
  }
`;
export const updateEc2Events = /* GraphQL */ `
  mutation UpdateEc2Events(
    $input: UpdateEc2EventsInput!
    $condition: ModelEc2EventsConditionInput
  ) {
    updateEc2Events(input: $input, condition: $condition) {
      id
      instanceId
      json
      expirationEpoch
      createdAt
      updatedAt
    }
  }
`;
export const deleteEc2Events = /* GraphQL */ `
  mutation DeleteEc2Events(
    $input: DeleteEc2EventsInput!
    $condition: ModelEc2EventsConditionInput
  ) {
    deleteEc2Events(input: $input, condition: $condition) {
      id
      instanceId
      json
      expirationEpoch
      createdAt
      updatedAt
    }
  }
`;
