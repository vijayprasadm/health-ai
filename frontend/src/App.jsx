import { useState } from "react";

function App() {
  const [form, setForm] = useState({
    name: "",
    weight: "",
    height: "",
    age: "",
    gender: "male",
    activity_level: 1,
    goal: "lose",
  });

  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const numericFields = ["weight", "height", "age", "activity_level"];
    setForm({
      ...form,
      [name]: numericFields.includes(name) ? Number(value) : value,
    });
  };

  const handleSubmit = async () => {
    try {
      const res = await fetch("/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error("API Error");
      const data = await res.json();
      setResult(data); // contains diet_plan + pdf_file
    } catch (err) {
      console.error(err);
      alert("Failed to calculate. Try again!");
    }
  };

  const downloadPDF = () => {
    if (!result) return;
    const link = document.createElement("a");
    link.href = `/pdfs/${result.pdf_file}`;
    link.download = result.pdf_file;
    link.click();
  };

  return (
    <div className="p-6 max-w-2xl mx-auto bg-gray-900 text-white rounded-lg mt-10">
      <h1 className="text-3xl font-bold mb-4">Health AI Dashboard</h1>

      {["name", "weight", "height", "age"].map((field) => (
        <div key={field} className="mb-2">
          <input
            type={["age", "weight", "height"].includes(field) ? "number" : "text"}
            name={field}
            placeholder={field.charAt(0).toUpperCase() + field.slice(1)}
            value={form[field]}
            onChange={handleChange}
            className="p-2 rounded text-black w-full"
          />
        </div>
      ))}

      <select name="gender" value={form.gender} onChange={handleChange} className="p-2 rounded text-black w-full mb-2">
        <option value="male">Male</option>
        <option value="female">Female</option>
      </select>

      <select name="activity_level" value={form.activity_level} onChange={handleChange} className="p-2 rounded text-black w-full mb-2">
        <option value={1}>Sedentary</option>
        <option value={2}>Low</option>
        <option value={3}>Moderate</option>
        <option value={4}>High</option>
        <option value={5}>Very High</option>
      </select>

      <select name="goal" value={form.goal} onChange={handleChange} className="p-2 rounded text-black w-full mb-4">
        <option value="lose">Lose Weight</option>
        <option value="gain">Gain Weight</option>
        <option value="maintain">Maintain Weight</option>
      </select>

      <button onClick={handleSubmit} className="bg-blue-600 px-4 py-2 rounded hover:bg-blue-700">
        Calculate
      </button>

      {result && (
        <div className="mt-6 bg-gray-800 p-4 rounded">
          <h2 className="text-xl font-bold mb-2">Your Daily Intake</h2>
          <p>Calories: {result.diet_plan.calories}</p>
          <p>Protein: {result.diet_plan.protein} g</p>
          <p>Fat: {result.diet_plan.fat} g</p>
          <p>Carbs: {result.diet_plan.carbs} g</p>
          <p>Water Intake: {result.diet_plan.water_intake_liters} L</p>
          <p>Steps Goal: {result.diet_plan.steps_goal} steps</p>

          <h3 className="mt-4 font-bold">Meal Plan:</h3>
          {Object.entries(result.diet_plan.meals).map(([meal, items]) => (
            <p key={meal}><strong>{meal}:</strong> {items.join(", ")}</p>
          ))}

          <button onClick={downloadPDF} className="mt-4 bg-green-600 px-4 py-2 rounded hover:bg-green-700">
            Download PDF
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
