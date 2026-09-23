export interface RegisterInput {
  email: string
  display_name: string
  password: string
}

export interface LoginInput {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}
