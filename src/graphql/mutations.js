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
