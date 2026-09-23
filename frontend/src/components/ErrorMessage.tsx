export function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="error-message" role="alert">
      {message}
    </div>
  )
}
