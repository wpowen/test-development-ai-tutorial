export function GET(request: Request) {
  return Response.redirect(new URL("/og.png", request.url), 307);
}
