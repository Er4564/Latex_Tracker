#!/bin/bash

# LaTeX Tracker - Linux Performance Monitor
# Monitors system resources and application performance

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔍 LaTeX Tracker Performance Monitor${NC}"
echo "===================================="

# Function to get process info
get_process_info() {
    local process_name="$1"
    local pid_file="$2"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            local cpu=$(ps -p $pid -o %cpu --no-headers | tr -d ' ')
            local mem=$(ps -p $pid -o %mem --no-headers | tr -d ' ')
            local rss=$(ps -p $pid -o rss --no-headers | tr -d ' ')
            local vsz=$(ps -p $pid -o vsz --no-headers | tr -d ' ')
            
            echo -e "   ${GREEN}✅ $process_name (PID: $pid)${NC}"
            echo "      CPU: ${cpu}% | Memory: ${mem}% | RSS: $((rss/1024))MB | VSZ: $((vsz/1024))MB"
        else
            echo -e "   ${RED}❌ $process_name (PID file exists but process not running)${NC}"
        fi
    else
        echo -e "   ${RED}❌ $process_name (No PID file)${NC}"
    fi
}

# System overview
echo -e "${BLUE}💻 System Resources:${NC}"
LOAD_AVG=$(uptime | awk -F'load average:' '{ print $2 }' | awk '{ print $1 }' | sed 's/,//')
UPTIME=$(uptime -p)
echo "   Load Average: $LOAD_AVG"
echo "   Uptime: $UPTIME"

# Memory information
echo ""
echo -e "${BLUE}💾 Memory Usage:${NC}"
free -h | grep -E "Mem|Swap" | while read line; do
    echo "   $line"
done

# Disk usage
echo ""
echo -e "${BLUE}💿 Disk Usage:${NC}"
df -h . | tail -1 | awk '{print "   " $1 ": " $3 " used, " $4 " available (" $5 " used)"}'

# MongoDB status
echo ""
echo -e "${BLUE}🍃 MongoDB:${NC}"
if pgrep -x "mongod" > /dev/null; then
    MONGO_PID=$(pgrep -x "mongod")
    MONGO_CPU=$(ps -p $MONGO_PID -o %cpu --no-headers | tr -d ' ')
    MONGO_MEM=$(ps -p $MONGO_PID -o %mem --no-headers | tr -d ' ')
    echo -e "   ${GREEN}✅ Running (PID: $MONGO_PID)${NC}"
    echo "      CPU: ${MONGO_CPU}% | Memory: ${MONGO_MEM}%"
    
    # MongoDB connections
    if command -v mongo &> /dev/null; then
        CONNECTIONS=$(mongo --quiet --eval "db.serverStatus().connections.current" 2>/dev/null || echo "N/A")
        echo "      Active Connections: $CONNECTIONS"
    fi
else
    echo -e "   ${RED}❌ Not running${NC}"
fi

# Application processes
echo ""
echo -e "${BLUE}🚀 Application Processes:${NC}"
get_process_info "Backend" "backend.pid"
get_process_info "Frontend" "frontend.pid"

# Network connections
echo ""
echo -e "${BLUE}🌐 Network Status:${NC}"
if command -v ss &> /dev/null; then
    BACKEND_LISTENING=$(ss -tlnp | grep ":8000" | wc -l)
    FRONTEND_LISTENING=$(ss -tlnp | grep ":3000" | wc -l)
    
    if [ $BACKEND_LISTENING -gt 0 ]; then
        echo -e "   ${GREEN}✅ Backend API (Port 8000): Listening${NC}"
    else
        echo -e "   ${RED}❌ Backend API (Port 8000): Not listening${NC}"
    fi
    
    if [ $FRONTEND_LISTENING -gt 0 ]; then
        echo -e "   ${GREEN}✅ Frontend (Port 3000): Listening${NC}"
    else
        echo -e "   ${RED}❌ Frontend (Port 3000): Not listening${NC}"
    fi
fi

# Log file sizes and recent activity
echo ""
echo -e "${BLUE}📋 Log Analysis:${NC}"
if [ -d "logs" ]; then
    for log_file in logs/*.log; do
        if [ -f "$log_file" ]; then
            LOG_SIZE=$(du -h "$log_file" | cut -f1)
            LOG_LINES=$(wc -l < "$log_file")
            LOG_NAME=$(basename "$log_file")
            echo "   $LOG_NAME: $LOG_SIZE ($LOG_LINES lines)"
            
            # Check for recent errors
            RECENT_ERRORS=$(tail -100 "$log_file" | grep -i "error\|exception\|failed" | wc -l)
            if [ $RECENT_ERRORS -gt 0 ]; then
                echo -e "      ${YELLOW}⚠️  $RECENT_ERRORS recent errors/exceptions${NC}"
            fi
        fi
    done
else
    echo "   No logs directory found"
fi

# Performance recommendations
echo ""
echo -e "${BLUE}💡 Performance Recommendations:${NC}"

# Check memory usage
FREE_MEM_PERCENT=$(free | awk 'NR==2{printf "%.1f", $7*100/$2}')
if (( $(echo "$FREE_MEM_PERCENT < 20" | bc -l) )); then
    echo -e "   ${YELLOW}⚠️  Low memory available (${FREE_MEM_PERCENT}%). Consider closing other applications.${NC}"
fi

# Check disk space
DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo -e "   ${YELLOW}⚠️  Disk usage high (${DISK_USAGE}%). Consider cleaning up temporary files.${NC}"
fi

# Check load average
LOAD_THRESHOLD=$(nproc)
if (( $(echo "$LOAD_AVG > $LOAD_THRESHOLD" | bc -l) )); then
    echo -e "   ${YELLOW}⚠️  High system load ($LOAD_AVG). Consider reducing concurrent processes.${NC}"
fi

echo ""
echo -e "${BLUE}🔄 Run this script periodically to monitor performance:${NC}"
echo "   watch -n 5 ./monitor.sh    # Update every 5 seconds"
echo "   ./monitor.sh > performance.log  # Save to file"
