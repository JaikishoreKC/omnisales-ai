export const getChatErrorMessage = (status) => {
  if (status === 429) {
    return 'We are getting a lot of requests. Please wait a moment and try again.'
  }
  if (status === 401) {
    return 'Chat is unavailable. Missing or invalid API key.'
  }
  return 'Sorry, something went wrong. Please try again.'
}
