# RC-Maps

Web app for the clubs fair: a 3D map of the stands, and a vote for the best club. Each student votes once with the code on their ticket, and results update live.

- Students: explore the stands in 3D, vote with their ticket code, see live results.
- Admins: manage clubs and students, import students from CSV, generate QR tickets, reset votes.
- JWT login, bcrypt password hashes, Helmet and rate limiting on the API.

Stack: React, Three.js (React Three Fiber), Vite and Tailwind on the front end; Node.js, Express and SQLite on the back end.

## Run it

```bash
cp .env.example backend/.env    # set JWT_SECRET and the first admin account
cd backend && npm install && npm start
cd ../frontend && npm install && npm run dev
```
