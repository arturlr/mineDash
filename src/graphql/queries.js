/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const getLoginAudit = /* GraphQL */ `
  query GetLoginAudit($id: ID!) {
    getLoginAudit(id: $id) {
      id
      email
      action
      expirationEpoch
      createdAt
      updatedAt
    }
  }
`;
export const listLoginAudits = /* GraphQL */ `
  query ListLoginAudits(
    $filter: ModelLoginAuditFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listLoginAudits(filter: $filter, limit: $limit, nextToken: $nextToken) {
      items {
        id
        email
        action
        expirationEpoch
        createdAt
        updatedAt
      }
      nextToken
    }
  }
`;
export const getEc2Events = /* GraphQL */ `
  query GetEc2Events($id: ID!) {
    getEc2Events(id: $id) {
      id
      instanceId
      json
      expirationEpoch
      createdAt
      updatedAt
    }
  }
`;
export const listEc2Events = /* GraphQL */ `
  query ListEc2Events(
    $filter: ModelEc2EventsFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listEc2Events(filter: $filter, limit: $limit, nextToken: $nextToken) {
      items {
        id
        instanceId
        json
        expirationEpoch
        createdAt
        updatedAt
      }
      nextToken
    }
  }
`;
