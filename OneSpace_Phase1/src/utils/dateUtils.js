export function formatFriendlyDate(dateStr, timeStr) {
  if (!dateStr) return "";

  const todayObj = new Date();
  const todayStr = todayObj.toISOString().slice(0, 10);
  
  const tomorrowObj = new Date();
  tomorrowObj.setDate(todayObj.getDate() + 1);
  const tomorrowStr = tomorrowObj.toISOString().slice(0, 10);

  const yesterdayObj = new Date();
  yesterdayObj.setDate(todayObj.getDate() - 1);
  const yesterdayStr = yesterdayObj.toISOString().slice(0, 10);

  let formattedTime = "";
  if (timeStr) {
    const parts = timeStr.split(":");
    if (parts.length >= 2) {
      const hour = parseInt(parts[0], 10);
      const min = parts[1];
      if (!isNaN(hour)) {
        const ampm = hour >= 12 ? "PM" : "AM";
        const displayHour = hour % 12 || 12;
        formattedTime = `${displayHour}:${min} ${ampm}`;
      } else {
        formattedTime = timeStr;
      }
    } else {
      formattedTime = timeStr;
    }
  }

  let baseDate = "";
  if (dateStr === todayStr) {
    baseDate = "Today";
  } else if (dateStr === tomorrowStr) {
    baseDate = "Tomorrow";
  } else if (dateStr === yesterdayStr) {
    baseDate = "Yesterday";
  } else {
    const d = new Date(dateStr + "T00:00:00");
    if (!isNaN(d.getTime())) {
      const weekday = d.toLocaleDateString("en-US", { weekday: "short" });
      const day = d.getDate();
      const month = d.toLocaleDateString("en-US", { month: "short" });
      baseDate = `${weekday}, ${day} ${month}`;
    } else {
      baseDate = dateStr;
    }
  }

  if (formattedTime) {
    return `${baseDate}, ${formattedTime}`;
  }
  return baseDate;
}
