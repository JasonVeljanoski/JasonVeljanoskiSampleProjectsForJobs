import { ValidationError } from './ValidationError'

export type HTTPValidationError = {
  detail?: Array<ValidationError>
}
