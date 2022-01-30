/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const onEc2ByInstance = /* GraphQL */ `
  subscription OnEc2ByInstance($name: String!) {
    onEc2ByInstance(name: $name) {
      id
      instanceId
      json
      expirationEpoch
      createdAt
      updatedAt
    }
  }
`;
export const onCreateLoginAudit = /* GraphQL */ `
  subscription OnCreateLoginAudit {
    onCreateLoginAudit {
      id
      email
      action
      expirationEpoch
      createdAt
      updatedAt
    }
  }
`;
export const onUpdateLoginAudit = /* GraphQL */ `
  subscription OnUpdateLoginAudit {
    onUpdateLoginAudit {
      id
      email
      action
      expirationEpoch
      createdAt
      updatedAt
    }
  }
`;
export const onDeleteLoginAudit = /* GraphQL */ `
  subscription OnDeleteLoginAudit {
    onDeleteLoginAudit {
      id
      email
      action
      expirationEpoch
      createdAt
      updatedAt
    }
  }
`;
export const onCreateEc2Events = /* GraphQL */ `
  subscription OnCreateEc2Events {
    onCreateEc2Events {
      id
      instanceId
      json
      expirationEpoch
      createdAt
      updatedAt
    }
  }
`;
export const onUpdateEc2Events = /* GraphQL */ `
  subscription OnUpdateEc2Events {
    onUpdateEc2Events {
      id
      instanceId
      json
      expirationEpoch
      createdAt
      updatedAt
    }
  }
`;
export const onDeleteEc2Events = /* GraphQL */ `
  subscription OnDeleteEc2Events {
    onDeleteEc2Events {
      id
      instanceId
      json
      expirationEpoch
      createdAt
      updatedAt
    }
  }
`;
