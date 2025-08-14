import { useEffect, useState } from "react";
import { useApi } from "../api/useApi.jsx";
import Card from "../components/Card.jsx";

export default function Courses() {
   const { listCourses } = useApi();
}
