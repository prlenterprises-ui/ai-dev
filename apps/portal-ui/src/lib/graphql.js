import { gql } from '@apollo/client'

// =============================================================================
// QUERIES
// =============================================================================

export const GET_HEALTH = gql`
  query GetHealth {
    health {
      status
      timestamp
      version
      modulesLoaded
    }
  }
`

export const GET_MODULES = gql`
  query GetModules {
    modules {
      id
      name
      description
      status
      icon
      route
    }
  }
`

export const GET_MODULE = gql`
  query GetModule($id: String!) {
    module(id: $id) {
      id
      name
      description
      status
      icon
      route
    }
  }
`

export const GET_APPLICATIONS = gql`
  query GetApplications($status: String) {
    applications(status: $status) {
      id
      jobTitle
      company
      status
      createdAt
      resumeUrl
      coverLetterUrl
    }
  }
`

// =============================================================================
// MUTATIONS
// =============================================================================

export const ASK_COUNCIL = gql`
  mutation AskCouncil($input: CouncilQueryInput!) {
    askCouncil(input: $input) {
      query
      individualResponses {
        model
        content
        tokensUsed
        latencyMs
      }
      rankings
      finalAnswer
      chairmanModel
    }
  }
`

export const MATCH_RESUME = gql`
  mutation MatchResume($input: ResumeMatchInput!) {
    matchResume(input: $input) {
      overallScore
      keywordMatch
      atsCompatibility
      suggestions
    }
  }
`

export const CREATE_APPLICATION = gql`
  mutation CreateApplication($input: JobApplicationInput!) {
    createApplication(input: $input) {
      id
      jobTitle
      company
      status
      createdAt
    }
  }
`

