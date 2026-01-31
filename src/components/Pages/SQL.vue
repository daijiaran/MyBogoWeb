<script setup>
/* eslint-disable no-undef */
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/api/user';

// SQL.js实例引用
let SQL = null;

// 持久化相关常量
const STORAGE_KEY = 'sql-practice-app';

// 历史操作记录
const history = ref([]);
const showHistory = ref(false);

// 添加历史记录
const addToHistory = (sql, success) => {
  if (!sql.trim() || !success) return;
  
  // 避免重复记录
  const lastRecord = history.value[history.value.length - 1];
  if (lastRecord && lastRecord.sql === sql) {
    return;
  }
  
  const record = {
    id: Date.now(),
    sql: sql,
    timestamp: new Date().toLocaleString(),
    user: currentUser.value
  };
  
  // 添加到历史记录开头
  history.value.unshift(record);
  
  // 限制历史记录数量
  if (history.value.length > 100) {
    history.value = history.value.slice(0, 100);
  }
  
  // 保存到localStorage
  saveHistoryToStorage();
};

// 从localStorage加载历史记录
const loadHistoryFromStorage = () => {
  try {
    const savedHistory = localStorage.getItem(STORAGE_KEY + '-history');
    if (savedHistory) {
      history.value = JSON.parse(savedHistory);
    }
  } catch (error) {
    console.error('加载历史记录失败:', error);
  }
};

// 保存历史记录到localStorage
const saveHistoryToStorage = () => {
  try {
    localStorage.setItem(STORAGE_KEY + '-history', JSON.stringify(history.value));
  } catch (error) {
    console.error('保存历史记录失败:', error);
  }
};

// 清空历史记录
const clearHistory = () => {
  history.value = [];
  saveHistoryToStorage();
};

const router = useRouter();
const db = ref(null);
const isReady = ref(false);
const errorMsg = ref('');
const queryStr = ref("-- 创建表\nCREATE TABLE students (\n  id INTEGER PRIMARY KEY,\n  name TEXT NOT NULL,\n  age INTEGER\n);\n\n-- 插入数据\nINSERT INTO students VALUES (1, '张三', 20);\nINSERT INTO students VALUES (2, '李四', 21);\n\n-- 授予权限\nGRANT SELECT, INSERT ON students TO user1;\n\n-- 查询数据\nSELECT * FROM students;");
const results = ref([]);
const executed = ref(false);
const isCompactMode = ref(false);

// 布局相关状态
const leftPanelWidth = ref(280);
const rightPanelWidth = ref(400);
const isResizingLeft = ref(false);
const isResizingRight = ref(false);
const resizeStartX = ref(0);
const resizeStartLeftWidth = ref(0);
const resizeStartRightWidth = ref(0);

// 主题切换相关
const isDark = ref(false);

// 应用主题
const applyThemeFromStorage = () => {
  const theme = localStorage.getItem('theme');
  isDark.value = theme === 'dark';
  if (isDark.value) {
    document.documentElement.setAttribute('data-theme', 'dark');
  } else {
    document.documentElement.removeAttribute('data-theme');
  }
};

// 切换主题
const toggleTheme = (event) => {
  const switchThemeLogic = () => {
    isDark.value = !isDark.value;
    if (isDark.value) {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('theme', 'light');
    }
  };
  if (!document.startViewTransition) {
    switchThemeLogic();
    return;
  }
  const x = event ? event.clientX : window.innerWidth / 2;
  const y = event ? event.clientY : 60;
  const endRadius = Math.hypot(
      Math.max(x, window.innerWidth - x),
      Math.max(y, window.innerHeight - y)
  );
  const transition = document.startViewTransition(switchThemeLogic);
  transition.ready.then(() => {
    document.documentElement.animate(
      [
        { clipPath: `circle(0px at ${x}px ${y}px)` },
        { clipPath: `circle(${endRadius}px at ${x}px ${y}px)` }
      ],
      {
        duration: 400,
        easing: 'ease-in-out'
      }
    );
  });
};

const users = ref([
  { name: 'root', permissions: {} }
]);
const currentUser = ref('root');
const showCreateUserModal = ref(false);
const newUserName = ref('');
/* eslint-disable no-unused-vars */
const tables = ref([]);
const selectedTable = ref(null);
const showTableStructure = ref(false);
const hoverTable = ref(null);
const activeTooltip = ref(null);
const tooltipPosition = ref({ top: 0, left: 0 });
/* eslint-enable no-unused-vars */

const toggleCompactMode = () => {
  isCompactMode.value = !isCompactMode.value;
  // 紧凑模式下固定左侧面板宽度
  if (isCompactMode.value) {
    leftPanelWidth.value = 60;
  } else {
    leftPanelWidth.value = 280;
  }
};

const showTooltip = (tableName, event) => {
  hoverTable.value = tableName;
  activeTooltip.value = tableName;
  
  // 获取table-item元素的位置
  const tableElement = event.currentTarget;
  const rect = tableElement.getBoundingClientRect();
  
  // 计算tooltip位置，确保不被窗口边缘裁剪
  const tooltipWidth = 300; // 估计的tooltip宽度
  const windowWidth = window.innerWidth;
  
  // 设置tooltip位置，默认显示在右侧
  tooltipPosition.value = {
    top: rect.top + window.scrollY + rect.height / 2 - 60, // 垂直居中
    left: rect.right + window.scrollX + 12 // 右侧12px
  };
  
  // 如果右侧空间不足，显示在左侧
  if (rect.right + tooltipWidth + 12 > windowWidth) {
    tooltipPosition.value.left = rect.left + window.scrollX - tooltipWidth - 12;
  }
};

const hideTooltip = () => {
  hoverTable.value = null;
  activeTooltip.value = null;
};

// 拖拽调整大小功能
const startLeftResize = (e) => {
  isResizingLeft.value = true;
  resizeStartX.value = e.clientX;
  resizeStartLeftWidth.value = leftPanelWidth.value;
  document.addEventListener('mousemove', handleLeftResize);
  document.addEventListener('mouseup', stopResize);
  e.preventDefault();
};

const startRightResize = (e) => {
  isResizingRight.value = true;
  resizeStartX.value = e.clientX;
  resizeStartRightWidth.value = rightPanelWidth.value;
  document.addEventListener('mousemove', handleRightResize);
  document.addEventListener('mouseup', stopResize);
  e.preventDefault();
};

const handleLeftResize = (e) => {
  if (!isResizingLeft.value) return;
  const deltaX = e.clientX - resizeStartX.value;
  // 限制最小宽度
  const newWidth = Math.max(60, resizeStartLeftWidth.value + deltaX);
  leftPanelWidth.value = newWidth;
  
  // 如果在紧凑模式下拖动，退出紧凑模式
  if (isCompactMode.value) {
    isCompactMode.value = false;
  }
};

const handleRightResize = (e) => {
  if (!isResizingRight.value) return;
  const deltaX = resizeStartX.value - e.clientX;
  // 限制最小宽度
  const newWidth = Math.max(300, resizeStartRightWidth.value + deltaX);
  rightPanelWidth.value = newWidth;
};

const stopResize = () => {
  isResizingLeft.value = false;
  isResizingRight.value = false;
  document.removeEventListener('mousemove', handleLeftResize);
  document.removeEventListener('mousemove', handleRightResize);
  document.removeEventListener('mouseup', stopResize);
};

// 保存数据到localStorage
const saveToLocalStorage = () => {
  try {
    // 准备需要保存的数据
    const dataToSave = {
      // 保存数据库状态（作为二进制数据）
      database: db.value ? Array.from(new Uint8Array(db.value.export())) : null,
      // 保存用户信息和权限
      users: users.value,
      currentUser: currentUser.value,
      // 保存SQL查询
      queryStr: queryStr.value,
      // 保存布局状态
      isCompactMode: isCompactMode.value,
      leftPanelWidth: leftPanelWidth.value,
      rightPanelWidth: rightPanelWidth.value
    };
    
    localStorage.setItem(STORAGE_KEY, JSON.stringify(dataToSave));
  } catch (error) {
    console.error('保存数据到localStorage失败:', error);
  }
};



// 从localStorage恢复数据
const restoreFromLocalStorage = async () => {
  try {
    const savedData = localStorage.getItem(STORAGE_KEY);
    if (savedData) {
      const parsedData = JSON.parse(savedData);
      
      // 等待SQL.js加载完成
      if (!db.value) {
        await initDatabase();
      }
      
      // 恢复数据库状态
      if (parsedData.database && db.value) {
        const uint8Array = new Uint8Array(parsedData.database);
        try {
          db.value = new SQL.Database(uint8Array);
          isReady.value = true;
        } catch (error) {
          console.error('恢复数据库失败，创建新数据库:', error);
          db.value = new SQL.Database();
        }
      }
      
      // 恢复用户信息
      if (parsedData.users && parsedData.users.length > 0) {
        users.value = parsedData.users;
      }
      
      // 恢复当前用户
      if (parsedData.currentUser) {
        currentUser.value = parsedData.currentUser;
      }
      
      // 恢复SQL查询
      if (parsedData.queryStr) {
        queryStr.value = parsedData.queryStr;
      }
      
      // 恢复布局状态
      if (parsedData.isCompactMode !== undefined) {
        isCompactMode.value = parsedData.isCompactMode;
      }
      
      if (parsedData.leftPanelWidth) {
        leftPanelWidth.value = parsedData.leftPanelWidth;
      }
      
      if (parsedData.rightPanelWidth) {
        rightPanelWidth.value = parsedData.rightPanelWidth;
      }
      
      // 更新表列表
      updateTablesList();
    } else {
      // 没有保存的数据，初始化新数据库
      await initDatabase();
    }
    
    // 加载历史记录
    loadHistoryFromStorage();
  } catch (error) {
    console.error('从localStorage恢复数据失败:', error);
    await initDatabase();
    // 加载历史记录
    loadHistoryFromStorage();
  }
};

const initDatabase = async () => {
  try {
    SQL = await initSqlJs({
      locateFile: () => 'https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/sql-wasm.wasm' 
    });
    
    db.value = new SQL.Database();
    isReady.value = true;
    updateTablesList();
    
    // 保存初始状态
    saveToLocalStorage();
  } catch (err) {
    console.error(err);
    errorMsg.value = "数据库引擎加载失败: " + err.message;
  }
};

const runQuery = () => {
  if (!db.value) return;
  errorMsg.value = '';
  results.value = [];
  executed.value = false;

  try {
    let sql = queryStr.value.trim();
    
    sql = sql.replace(/--.*$/gm, '');
    
    const statements = sql.split(';').filter(s => s.trim().length > 0);
    const allResults = [];
    
    for (const statement of statements) {
      const stmt = statement.trim();
      
      if (!stmt) continue;
      
      const grantMatch = stmt.match(/^GRANT\s+([\w\s,]+)\s+ON\s+([\w_]+)\s+TO\s+([\w_]+)(?:\s+WITH\s+GRANT\s+OPTION)?/i);
      if (grantMatch) {
        const grantResult = handleGrant(grantMatch);
        if (grantResult.error) {
          errorMsg.value = grantResult.error;
          return;
        }
        allResults.push(grantResult);
        continue;
      }
      
      const revokeMatch = stmt.match(/^REVOKE\s+([\w\s,]+)\s+ON\s+([\w_]+)\s+FROM\s+([\w_]+)/i);
      if (revokeMatch) {
        const revokeResult = handleRevoke(revokeMatch);
        if (revokeResult.error) {
          errorMsg.value = revokeResult.error;
          return;
        }
        allResults.push(revokeResult);
        continue;
      }
      
      // 数据类型验证：处理各种ALTER TABLE语句
      // 1. ALTER TABLE ... ADD (添加字段)
      // 2. ALTER TABLE ... MODIFY (修改字段类型/属性)
      // 3. ALTER TABLE ... CHANGE (修改字段名、类型/属性)
      const alterTableMatch = stmt.match(/^ALTER\s+TABLE\s+(\w+)\s+(ADD|MODIFY|CHANGE)/i);
      if (alterTableMatch) {
        const alterAction = alterTableMatch[2].toUpperCase();
        
        // 处理ADD子句
        if (alterAction === 'ADD') {
          const addMatch = stmt.match(/ADD\s+\w+\s+([\w_]+)/i);
          if (addMatch) {
            const dataType = addMatch[1].toUpperCase();
            if (!validateDataType(dataType)) {
              return;
            }
          }
        }
        // 处理MODIFY子句
        else if (alterAction === 'MODIFY') {
          const modifyMatch = stmt.match(/MODIFY\s+\w+\s+([\w_]+)/i);
          if (modifyMatch) {
            const dataType = modifyMatch[1].toUpperCase();
            if (!validateDataType(dataType)) {
              return;
            }
          }
        }
        // 处理CHANGE子句
        else if (alterAction === 'CHANGE') {
          const changeMatch = stmt.match(/CHANGE\s+\w+\s+\w+\s+([\w_]+)/i);
          if (changeMatch) {
            const dataType = changeMatch[1].toUpperCase();
            if (!validateDataType(dataType)) {
              return;
            }
          }
        }
      }
      
      // CREATE TABLE语句的数据类型验证
      const createTableTypeMatch = stmt.match(/^CREATE\s+TABLE\s+(\w+)\s*\(([\s\S]*?)\)/i);
      if (createTableTypeMatch) {
        const columnsPart = createTableTypeMatch[2];
        
        // 使用正则表达式直接匹配列定义和数据类型
        // 匹配模式：列名 数据类型(可选参数) 约束条件
        const columnTypeRegex = /\s*(\w+)\s+([\w_]+(?:\([^)]*\))?)\s*/gi;
        
        // 重置lastIndex以确保从头开始匹配
        columnTypeRegex.lastIndex = 0;
        
        let match;
        while ((match = columnTypeRegex.exec(columnsPart)) !== null) {
          const fullDataType = match[2];
          
          // 验证数据类型
          if (!validateDataType(fullDataType)) {
            return;
          }
        }
      }
      
      // CAST和CONVERT函数的数据类型验证
      const castMatch = stmt.match(/CAST\s*\(.*?AS\s+([\w_]+)\)/gi);
      if (castMatch) {
        for (const match of castMatch) {
          const typeMatch = match.match(/AS\s+([\w_]+)/i);
          if (typeMatch) {
            const dataType = typeMatch[1].toUpperCase();
            if (!validateDataType(dataType)) {
              return;
            }
          }
        }
      }
      
      const convertMatch = stmt.match(/CONVERT\s*\(.*?,\s*([\w_]+)\)/gi);
      if (convertMatch) {
        for (const match of convertMatch) {
          const typeMatch = match.match(/,\s*([\w_]+)\)/i);
          if (typeMatch) {
            const dataType = typeMatch[1].toUpperCase();
            if (!validateDataType(dataType)) {
              return;
            }
          }
        }
      }
      

      
      // 权限检查：除了GRANT和REVOKE语句外，其他语句需要检查权限
      if (currentUser.value !== 'root') {
        const parsedStmt = parseSQLStatement(stmt);
        if (parsedStmt) {
          const { operation, table } = parsedStmt;
          const user = users.value.find(u => u.name === currentUser.value);
          const userPerms = user.permissions[table] || [];
          
          // 映射操作到权限
          let requiredPermission;
          switch (operation) {
            case 'SELECT':
              requiredPermission = 'SELECT';
              break;
            case 'INSERT':
              requiredPermission = 'INSERT';
              break;
            case 'UPDATE':
              requiredPermission = 'UPDATE';
              break;
            case 'DELETE':
              requiredPermission = 'DELETE';
              break;
            case 'CREATE TABLE':
            case 'ALTER TABLE':
            case 'DROP TABLE':
              requiredPermission = 'ALTER';
              break;
            default:
              // 其他操作默认允许（或根据需要添加更多检查）
              requiredPermission = null;
          }
          
          if (requiredPermission) {
            const hasPermission = userPerms.some(p => p.name === requiredPermission);
            if (!hasPermission) {
              errorMsg.value = `当前用户没有权限执行 ${operation} 操作在表 ${table} 上`;
              return;
            }
          }
        }
      }
      
      try {
        const res = db.value.exec(stmt);
        if (res && res.length > 0) {
          allResults.push(...res);
        }
      } catch (execErr) {
        errorMsg.value = execErr.message;
        return;
      }
    }
    
    results.value = allResults;
    executed.value = true;
    updateTablesList();
    
    // 记录历史操作
    addToHistory(queryStr.value, true);
    
    // 执行查询后保存数据
    saveToLocalStorage();
  } catch (err) {
    errorMsg.value = err.message;
    // 查询失败不记录到历史
  }
};

const handleGrant = (match) => {
  const permissions = match[1].split(',').map(p => p.trim().toUpperCase());
  const tableName = match[2];
  const userName = match[3];
  const hasGrantOption = match[0].toLowerCase().includes('with grant option');
  
  if (!users.value.find(u => u.name === userName)) {
    return { error: `用户 ${userName} 不存在` };
  }
  
  // 检查当前用户是否有权限授予
  if (currentUser.value !== 'root') {
    const currentUserObj = users.value.find(u => u.name === currentUser.value);
    const currentUserPerms = currentUserObj.permissions[tableName] || [];
    
    for (const perm of permissions) {
      // 查找当前用户是否有该权限，并且有授予选项
      const hasPermission = currentUserPerms.some(p => 
        p.name === perm && p.withGrantOption
      );
      
      if (!hasPermission) {
        return { error: `当前用户没有权限授予 ${perm} 权限给 ${userName}` };
      }
    }
  }
  
  const user = users.value.find(u => u.name === userName);
  if (!user.permissions[tableName]) {
    user.permissions[tableName] = [];
  }
  
  const grantedPermissions = [];
  permissions.forEach(perm => {
    // 检查用户是否已经有该权限
    const existingPermIndex = user.permissions[tableName].findIndex(p => p.name === perm);
    
    if (existingPermIndex >= 0) {
      // 更新现有权限的授予选项
      if (hasGrantOption) {
        user.permissions[tableName][existingPermIndex].withGrantOption = true;
      }
    } else {
      // 添加新权限
      user.permissions[tableName].push({
        name: perm,
        withGrantOption: hasGrantOption,
        grantedBy: currentUser.value,
        grantedUsers: []
      });
    }
    
    grantedPermissions.push(perm);
  });
  
  // 记录当前用户对该用户的权限授予关系
  if (currentUser.value !== 'root' && currentUser.value !== userName) {
    const grantor = users.value.find(u => u.name === currentUser.value);
    if (!grantor.permissions[tableName]) {
      grantor.permissions[tableName] = [];
    }
    
    for (const perm of permissions) {
      const grantorPerm = grantor.permissions[tableName].find(p => p.name === perm);
      if (grantorPerm && !grantorPerm.grantedUsers.includes(userName)) {
        grantorPerm.grantedUsers.push(userName);
      }
    }
  }
  
  let message = `已授予 ${userName} 对表 ${tableName} 的权限: ${grantedPermissions.join(', ')}`;
  if (hasGrantOption) {
    message += ' (带授权选项)';
  }
  
  return {
    columns: ['message'],
    values: [[message]]
  };
};

// SQL语句解析函数，用于识别操作类型和目标表
const parseSQLStatement = (stmt) => {
  const trimmedStmt = stmt.trim().toLowerCase();
  
  // 处理SELECT语句 - 使用[\s\S]匹配包括换行符在内的所有字符
  const selectMatch = trimmedStmt.match(/^select[\s\S]*?from\s+([\w_]+)/);
  if (selectMatch) {
    return { operation: 'SELECT', table: selectMatch[1] };
  }
  
  // 处理INSERT语句
  const insertMatch = trimmedStmt.match(/^insert\s+into\s+([\w_]+)/);
  if (insertMatch) {
    return { operation: 'INSERT', table: insertMatch[1] };
  }
  
  // 处理UPDATE语句
  const updateMatch = trimmedStmt.match(/^update\s+([\w_]+)/);
  if (updateMatch) {
    return { operation: 'UPDATE', table: updateMatch[1] };
  }
  
  // 处理DELETE语句 - 使用[\s\S]匹配包括换行符在内的所有字符
  const deleteMatch = trimmedStmt.match(/^delete[\s\S]*?from\s+([\w_]+)/);
  if (deleteMatch) {
    return { operation: 'DELETE', table: deleteMatch[1] };
  }
  
  // 处理CREATE TABLE语句
  const createTableMatch = trimmedStmt.match(/^create\s+table\s+([\w_]+)/);
  if (createTableMatch) {
    return { operation: 'CREATE TABLE', table: createTableMatch[1] };
  }
  
  // 处理DROP TABLE语句
  const dropTableMatch = trimmedStmt.match(/^drop\s+table\s+([\w_]+)/);
  if (dropTableMatch) {
    return { operation: 'DROP TABLE', table: dropTableMatch[1] };
  }
  
  // 处理ALTER TABLE语句
  const alterTableMatch = trimmedStmt.match(/^alter\s+table\s+([\w_]+)/);
  if (alterTableMatch) {
    return { operation: 'ALTER TABLE', table: alterTableMatch[1] };
  }
  
  // 无法解析的语句
  return null;
};

// 数据类型验证辅助函数
const validateDataType = (dataType) => {
  // 定义支持的数据类型和别名映射
  const dataTypeAliases = {
    // 数值类型
    'INTEGER': ['INT', 'SMALLINT', 'TINYINT', 'MEDIUMINT', 'BIGINT', 'BIT'],
    'REAL': ['FLOAT', 'DOUBLE', 'DECIMAL', 'NUMERIC', 'DOUBLE PRECISION'],
    // 字符串类型
    'TEXT': ['CHAR', 'VARCHAR', 'CLOB', 'CHARACTER', 'NVARCHAR', 'NCHAR', 'TEXT', 'LONGTEXT'],
    // 二进制类型
    'BLOB': ['BINARY', 'VARBINARY', 'TINYBLOB', 'BLOB', 'MEDIUMBLOB', 'LONGBLOB'],
    // 日期时间类型
    'DATE': [],
    'DATETIME': ['TIMESTAMP', 'TIME', 'YEAR', 'DATETIME'],
    // 布尔类型
    'BOOLEAN': ['BOOL', 'TINYINT(1)']
  };
  
  // 提取基础类型（去除括号和参数）
  const baseType = dataType.replace(/\(.*\)/, '').toUpperCase();
  
  // 检查是否为有效的数据类型或别名
  let isValid = false;
  for (const [validType, aliases] of Object.entries(dataTypeAliases)) {
    if (validType === baseType || aliases.includes(baseType)) {
      isValid = true;
      break;
    }
  }
  
  // 检查是否为NULL类型
  if (baseType === 'NULL') {
    isValid = true;
  }
  
  if (!isValid) {
    const allValidTypes = [...Object.keys(dataTypeAliases), ...Object.values(dataTypeAliases).flat()].filter((v, i, a) => a.indexOf(v) === i);
    errorMsg.value = `无效的数据类型: ${dataType}。支持的数据类型包括: ${allValidTypes.sort().join(', ')}`;
    return false;
  }
  return true;
};

// 级联移除权限的辅助函数
const cascadeRevokePermissions = (userName, tableName, permissions) => {
  const user = users.value.find(u => u.name === userName);
  if (!user || !user.permissions[tableName]) {
    return;
  }
  
  // 移除用户的指定权限
  const revokedPermissions = [];
  permissions.forEach(perm => {
    const permIndex = user.permissions[tableName].findIndex(p => p.name === perm);
    if (permIndex >= 0) {
      // 获取要移除的权限对象
      const removedPerm = user.permissions[tableName][permIndex];
      
      // 如果该权限有授予选项，级联移除被授予用户的权限
      if (removedPerm.withGrantOption && removedPerm.grantedUsers.length > 0) {
        // 递归移除被授予用户的相同权限
        removedPerm.grantedUsers.forEach(grantedUserName => {
          cascadeRevokePermissions(grantedUserName, tableName, [perm]);
        });
      }
      
      // 从权限列表中移除该权限
      user.permissions[tableName].splice(permIndex, 1);
      revokedPermissions.push(perm);
      
      // 更新授权者的grantedUsers列表
      if (removedPerm.grantedBy && removedPerm.grantedBy !== 'root' && removedPerm.grantedBy !== userName) {
        const grantor = users.value.find(u => u.name === removedPerm.grantedBy);
        if (grantor && grantor.permissions[tableName]) {
          const grantorPerm = grantor.permissions[tableName].find(p => p.name === perm);
          if (grantorPerm && grantorPerm.grantedUsers.includes(userName)) {
            grantorPerm.grantedUsers = grantorPerm.grantedUsers.filter(u => u !== userName);
          }
        }
      }
    }
  });
  
  // 如果该表没有权限了，删除该表的权限记录
  if (user.permissions[tableName].length === 0) {
    delete user.permissions[tableName];
  }
  
  return revokedPermissions;
};

const handleRevoke = (match) => {
  const permissions = match[1].split(',').map(p => p.trim().toUpperCase());
  const tableName = match[2];
  const userName = match[3];
  
  if (!users.value.find(u => u.name === userName)) {
    return { error: `用户 ${userName} 不存在` };
  }
  
  const user = users.value.find(u => u.name === userName);
  if (!user.permissions[tableName]) {
    return { error: `用户 ${userName} 对表 ${tableName} 没有任何权限` };
  }
  
  // 检查当前用户是否有权限撤销
  if (currentUser.value !== 'root' && currentUser.value !== userName) {
    // 只有root用户或权限所有者可以撤销权限
    return { error: `当前用户没有权限撤销 ${userName} 的权限` };
  }
  
  // 执行级联权限移除
  const revokedPermissions = cascadeRevokePermissions(userName, tableName, permissions);
  
  if (revokedPermissions.length === 0) {
    return { error: `用户 ${userName} 没有指定的权限` };
  }
  
  return {
    columns: ['message'],
    values: [[`已撤销 ${userName} 对表 ${tableName} 的权限: ${revokedPermissions.join(', ')}`]]
  };
};

const resetDb = async () => {
    if(db.value) db.value.close();
    await initDatabase();
    queryStr.value = "SELECT 'Reset Successful' as status;";
    runQuery();
    // 重置数据库后保存数据
    saveToLocalStorage();
}

const updateTablesList = () => {
  if (!db.value) return;
  try {
    const res = db.value.exec("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'");
    tables.value = res[0] ? res[0].values.map(row => row[0]) : [];
  } catch (err) {
    console.error("获取表列表失败:", err);
  }
};

const getTableStructure = (tableName) => {
  if (!db.value) return null;
  try {
    const res = db.value.exec(`PRAGMA table_info(${tableName})`);
    return res[0] ? res[0].values.map(row => ({
      cid: row[0],
      name: row[1],
      type: row[2],
      notnull: row[3],
      dflt_value: row[4],
      pk: row[5]
    })) : [];
  } catch (err) {
    console.error("获取表结构失败:", err);
    return null;
  }
};

const getForeignKeys = (tableName) => {
  if (!db.value) return [];
  try {
    const res = db.value.exec(`PRAGMA foreign_key_list(${tableName})`);
    return res[0] ? res[0].values.map(row => ({
      id: row[0],
      table: row[2],
      from: row[3],
      to: row[4],
      on_update: row[5],
      on_delete: row[6]
    })) : [];
  } catch (err) {
    console.error("获取外键失败:", err);
    return [];
  }
};

/* eslint-disable no-unused-vars */
const selectTable = (tableName) => {
  selectedTable.value = tableName;
  showTableStructure.value = true;
};
/* eslint-enable no-unused-vars */

/* eslint-disable no-unused-vars */
const showTableData = (tableName) => {
  if (!db.value) return;
  try {
    const res = db.value.exec(`SELECT * FROM ${tableName}`);
    if (res && res.length > 0) {
      results.value = res;
      executed.value = true;
      errorMsg.value = '';
    } else {
      errorMsg.value = `表 ${tableName} 为空`;
      results.value = [];
      executed.value = false;
    }
  } catch (err) {
    errorMsg.value = `查询表 ${tableName} 失败: ${err.message}`;
    results.value = [];
    executed.value = false;
  }
};
/* eslint-enable no-unused-vars */

const closeTableStructure = () => {
  selectedTable.value = null;
  showTableStructure.value = false;
};

const createUser = () => {
  if (!newUserName.value.trim()) return;
  if (users.value.find(u => u.name === newUserName.value)) {
    alert('用户名已存在');
    return;
  }
  users.value.push({
    name: newUserName.value,
    permissions: {}
  });
  newUserName.value = '';
  showCreateUserModal.value = false;
};

const deleteUser = (userName) => {
  if (userName === 'root') {
    alert('无法删除 root 用户');
    return;
  }
  if (confirm(`确定要删除用户 ${userName} 吗？`)) {
    users.value = users.value.filter(u => u.name !== userName);
  }
};

const switchUser = (userName) => {
  currentUser.value = userName;
};

const getUserPermissions = (user) => {
  const perms = [];
  Object.keys(user.permissions).forEach(tableName => {
    const tablePerms = user.permissions[tableName];
    if (tablePerms && tablePerms.length > 0) {
      perms.push(`${tableName}：${tablePerms.join(', ')}`);
    }
  });
  
  if (user.name === 'root') {
    return '所有表的所有权限';
  }
  
  return perms.length > 0 ? perms.join(' | ') : '无权限';
};

const tableStructure = computed(() => {
  if (!selectedTable.value) return null;
  return {
    columns: getTableStructure(selectedTable.value),
    foreignKeys: getForeignKeys(selectedTable.value)
  };
});

onMounted(() => {
  // 登录状态检测
  const userStore = useUserStore();
  if (!userStore.isLogin) {
    router.push('/');
    return;
  }

  const script = document.createElement('script');
  script.src = 'https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/sql-wasm.js';
  script.async = true;
  script.onload = () => {
    restoreFromLocalStorage();
    // 应用主题
    applyThemeFromStorage();
  };
  script.onerror = () => {
    errorMsg.value = "无法加载 SQL.js 库";
  };
  document.head.appendChild(script);
});

// 监听数据变化并自动保存
watch([users, currentUser, queryStr, isCompactMode, leftPanelWidth, rightPanelWidth], () => {
  // 使用setTimeout延迟保存，避免频繁操作影响性能
  setTimeout(() => {
    saveToLocalStorage();
  }, 500);
}, { deep: true });
</script>

<template>
  <div class="sql-page-container">
    <header class="sql-header">
      <div class="header-left">
        <button class="btn secondary sm" @click="router.push('/quiz-app-container')">
          ← 返回刷题
        </button>
        <h1>💾 SQL 语法练习</h1>
      </div>
      <div class="header-right">
        <span v-if="!isReady" class="status loading">⏳ 引擎加载中...</span>
        <span v-else class="status ready">✅ 引擎就绪</span>
        <button class="theme-toggle" @click="toggleTheme" title="切换深色/浅色模式">
          {{ isDark ? '☀️' : '🌙' }}
        </button>
      </div>
    </header>

    <div class="user-bar">
      <div class="user-list">
        <div 
          v-for="user in users" 
          :key="user.name"
          class="user-item"
          :class="{ active: currentUser === user.name }"
          @click="switchUser(user.name)"
        >
          <span class="user-icon">👤</span>
          <span class="user-name">{{ user.name }}</span>
          <div class="user-permissions-tooltip">
            <div class="tooltip-content">
              <strong>{{ user.name }} 的权限:</strong>
              <p>{{ getUserPermissions(user) }}</p>
            </div>
          </div>
          <button 
            v-if="user.name !== 'root'" 
            class="delete-user-btn"
            @click.stop="deleteUser(user.name)"
          >
            ×
          </button>
        </div>
        <button class="btn primary sm create-user-btn" @click="showCreateUserModal = true">
          + 创建用户
        </button>
      </div>
    </div>

    <div class="sql-main" :class="{ resizing: isResizingLeft || isResizingRight }">
      <!-- 左侧面板：数据库对象 -->
      <aside 
        class="database-sidebar" 
        :class="{ compact: isCompactMode }"
        :style="{ width: leftPanelWidth + 'px' }"
      >
        <div class="sidebar-header">
          <h3>📁 数据库对象</h3>
          <button class="compact-toggle-btn" @click="toggleCompactMode" title="紧凑模式">
            {{ isCompactMode ? '📐' : '📏' }}
          </button>
        </div>
        <div class="table-list">
          <div class="table-list-scrollable">
            <div 
              v-for="table in tables" 
              :key="table"
              class="table-item"
              @click="showTableData(table)"
              @mouseenter="showTooltip(table, $event)"
              @mouseleave="hideTooltip"
            >
              <span class="table-icon">📋</span>
              <span class="table-name">{{ table }}</span>
            </div>
            <div v-if="tables.length === 0" class="empty-state">
              暂无表
            </div>
          </div>
        </div>
      </aside>

      <!-- 左侧拖拽分界线 -->
      <div 
        class="resize-handle left-resize"
        @mousedown="startLeftResize"
        :style="{ left: leftPanelWidth + 'px' }"
      ></div>

      <!-- 中间面板：结果展示 -->
      <div class="middle-section">
        <div class="result-section">
          <div v-if="errorMsg" class="message error">
            <strong>❌ 错误:</strong> {{ errorMsg }}
          </div>
          
          <div v-else-if="executed && results.length === 0" class="message success">
            ✨ 执行成功 (无返回结果)
          </div>

          <div v-for="(res, index) in results" :key="index" class="result-table-wrapper">
            <table class="result-table">
              <thead>
                <tr>
                  <th v-for="col in res.columns" :key="col">{{ col }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, rIndex) in res.values" :key="rIndex">
                  <td v-for="(val, cIndex) in row" :key="cIndex">{{ val }}</td>
                </tr>
              </tbody>
            </table>
            <div class="result-meta">{{ res.values.length }} 行结果</div>
          </div>
        </div>
        
        <!-- 历史操作记录面板 -->
        <div v-if="showHistory" class="history-panel">
          <div class="history-header">
            <h3>📜 历史操作记录</h3>
            <div class="history-actions">
              <button class="btn sm" @click="clearHistory">清空历史</button>
              <button class="btn sm close-btn" @click="showHistory = false">✕</button>
            </div>
          </div>
          <div class="history-list">
            <div v-if="history.length === 0" class="empty-history">
              暂无历史操作记录
            </div>
            <div 
              v-for="record in history" 
              :key="record.id" 
              class="history-item"
              @click="queryStr = record.sql"
            >
              <div class="history-info">
                <div class="history-timestamp">{{ record.timestamp }}</div>
                <div class="history-user">{{ record.user }}</div>
              </div>
              <div class="history-sql">{{ record.sql }}</div>
              <div class="history-action">
                <span class="select-btn">点击使用</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧拖拽分界线 -->
      <div 
        class="resize-handle right-resize"
        @mousedown="startRightResize"
        :style="{ right: rightPanelWidth + 'px' }"
      ></div>

      <!-- 右侧面板：SQL编辑器 -->
      <aside class="editor-sidebar" :style="{ width: rightPanelWidth + 'px' }">
        <div class="toolbar">
          <button class="btn primary" @click="runQuery" :disabled="!isReady">▶ 运行 (Run)</button>
          <button class="btn secondary" @click="resetDb" :disabled="!isReady">↺ 重置数据库</button>
          <button class="btn secondary" @click="showHistory = !showHistory" :disabled="!isReady">📜 历史操作</button>
        </div>
        <textarea 
          v-model="queryStr" 
          class="sql-editor" 
          placeholder="请输入 SQL 语句...&#10;&#10;支持 GRANT/REVOKE 语法:&#10;GRANT SELECT, INSERT ON 表名 TO 用户名;&#10;REVOKE SELECT ON 表名 FROM 用户名;"
          spellcheck="false"
        ></textarea>
      </aside>

      <!-- 全局tooltip，显示在页面顶层 -->
      <div 
        v-if="activeTooltip" 
        class="table-tooltip" 
        :style="{
          top: tooltipPosition.top + 'px',
          left: tooltipPosition.left + 'px'
        }"
      >
        <div class="tooltip-content">
          <div class="tooltip-header">📊 {{ activeTooltip }} - 列信息</div>
          <div class="tooltip-body">
            <div v-if="getTableStructure(activeTooltip) && getTableStructure(activeTooltip).length > 0">
              <div v-for="col in getTableStructure(activeTooltip)" :key="col.cid" class="column-info">
                <span class="col-name">{{ col.name }}</span>
                <span class="col-type">{{ col.type || 'ANY' }}</span>
                <span v-if="col.pk" class="col-pk">🔑</span>
              </div>
            </div>
            <div v-else class="no-columns">暂无列信息</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showTableStructure && tableStructure" class="modal-overlay" @click="closeTableStructure">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>📋 表结构: {{ selectedTable }}</h3>
          <button class="modal-close" @click="closeTableStructure">×</button>
        </div>
        <div class="modal-body">
          <div v-if="tableStructure.columns.length > 0" class="structure-section">
            <h4>列信息</h4>
            <table class="structure-table">
              <thead>
                <tr>
                  <th>列名</th>
                  <th>类型</th>
                  <th>非空</th>
                  <th>默认值</th>
                  <th>主键</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="col in tableStructure.columns" :key="col.cid">
                  <td>{{ col.name }}</td>
                  <td>{{ col.type || '-' }}</td>
                  <td>{{ col.notnull ? '是' : '否' }}</td>
                  <td>{{ col.dflt_value || '-' }}</td>
                  <td>
                    <span v-if="col.pk" class="pk-badge">🔑 PK</span>
                    <span v-else>-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="tableStructure.foreignKeys.length > 0" class="structure-section">
            <h4>外键约束</h4>
            <table class="structure-table">
              <thead>
                <tr>
                  <th>列</th>
                  <th>引用表</th>
                  <th>引用列</th>
                  <th>更新</th>
                  <th>删除</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="fk in tableStructure.foreignKeys" :key="fk.id">
                  <td>{{ fk.from }}</td>
                  <td>{{ fk.table }}</td>
                  <td>{{ fk.to }}</td>
                  <td>{{ fk.on_update || '-' }}</td>
                  <td>{{ fk.on_delete || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="tableStructure.foreignKeys.length === 0 && tableStructure.columns.length === 0" class="empty-state">
            暂无表结构信息
          </div>
        </div>
      </div>
    </div>

    <div v-if="showCreateUserModal" class="modal-overlay" @click="showCreateUserModal = false">
      <div class="modal-content small" @click.stop>
        <div class="modal-header">
          <h3>创建新用户</h3>
          <button class="modal-close" @click="showCreateUserModal = false">×</button>
        </div>
        <div class="modal-body">
          <input 
            v-model="newUserName" 
            type="text" 
            class="input-field"
            placeholder="输入用户名"
            @keyup.enter="createUser"
          >
          <div class="modal-actions">
            <button class="btn secondary" @click="showCreateUserModal = false">取消</button>
            <button class="btn primary" @click="createUser">创建</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
/* 定义全局变量，确保样式穿透 */
:root {
  --primary: #4a7c59;
  --primary-hover: #3a6345;
  --success: #609966;
  --danger: #cf5c5c;
  --warning: #d4a373;
  --bg: #f7f7f4;
  --card-bg: #ffffff;
  --text: #2d3436;
  --text-secondary: #636e72;
  --text-light: #b2bec3;
  --border: #e6e6e2;
  --border-light: #f0f0ed;
  --input-bg: #fafaf9;
  --shadow: 0 4px 20px -2px rgba(45, 52, 54, 0.08);
  --shadow-lg: 0 10px 15px -3px rgba(45, 52, 54, 0.1);
  --sidebar-width: 280px;
  --header-height: 64px;

  /* 滚动条专用变量 (浅色模式) */
  --scrollbar-track: transparent;
  --scrollbar-thumb: #c8c8c6;
  --scrollbar-thumb-hover: #a0a09e;
  --scrollbar-width: 10px;
}
/* Dark Mode 适配 */
[data-theme="dark"] {
  --primary: #8ebf95;
  --primary-hover: #4a7c59;
  --success: #609966;
  --danger: #cf5c5c;
  --warning: #d4a373;
  --bg: #1c1c1c;
  --card-bg: #262626;
  --text: #e0e0e0;
  --text-secondary: #a3a3a3;
  --text-light: #b2bec3;
  --border: #333333;
  --border-light: #404040;
  --input-bg: #2d2d2d;
  --shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3);

  /* 滚动条专用变量 (深色模式) */
  --scrollbar-track: transparent;
  --scrollbar-thumb: #404040;
  --scrollbar-thumb-hover: #505050;
}
</style>

<style scoped>
.sql-page-container {
  min-height: 100vh;
  background-color: var(--bg, #f7f7f4);
  color: var(--text, #2d3436);
  font-family: 'Inter', sans-serif;
  display: flex;
  flex-direction: column;
}

.sql-header {
  height: 64px;
  background-color: var(--card-bg, #ffffff);
  border-bottom: 1px solid var(--border, #e6e6e2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.sql-header h1 {
  font-size: 1.2rem;
  margin: 0;
  font-weight: 600;
  color: var(--text, #2d3436);
}

.status {
  font-size: 0.9rem;
  font-weight: 500;
}
.status.loading { color: var(--warning, #d4a373); }
.status.ready { color: var(--success, #609966); }

/* 主题切换按钮样式 */
.theme-toggle {
  background: var(--card-bg);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 10px 14px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1.3rem;
  outline: none;
  transition: all 0.3s ease;
  flex-shrink: 0;
  margin-left: 16px;
}

.theme-toggle:hover {
  background-color: var(--bg);
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.theme-toggle:active {
  transform: scale(0.98);
}

.user-bar {
  background-color: var(--card-bg, #ffffff);
  border-bottom: 1px solid var(--border, #e6e6e2);
  padding: 12px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-list {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.user-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: var(--input-bg, #fafaf9);
  border: 1px solid var(--border, #e6e6e2);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.user-item:hover {
  background-color: var(--bg, #f0f0f0);
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.user-item.active {
  background-color: var(--primary, #4a7c59);
  color: white;
  border-color: var(--primary, #4a7c59);
}

.user-icon {
  font-size: 1.2rem;
}

.user-name {
  font-weight: 500;
}

.user-permissions-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 8px;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s;
  z-index: 100;
}

.user-item:hover .user-permissions-tooltip {
  opacity: 1;
  visibility: visible;
}

.tooltip-content {
  background-color: #333;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  min-width: 200px;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  white-space: pre-wrap;
  word-break: break-all;
}

.tooltip-content strong {
  display: block;
  margin-bottom: 4px;
  color: #fff;
}

.tooltip-content p {
  margin: 0;
  color: #ccc;
  line-height: 1.4;
}

.delete-user-btn {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: var(--danger, #cf5c5c);
  color: white;
  border: none;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  opacity: 0;
  transition: opacity 0.2s;
}

.user-item:hover .delete-user-btn {
  opacity: 1;
}

.delete-user-btn:hover {
  background-color: #b04a4a;
}

.create-user-btn {
  border-radius: 20px;
}

.sql-main {
  flex: 1;
  display: flex;
  gap: 0;
  overflow: hidden;
  position: relative;
}

/* 中间面板：结果展示 */
.middle-section {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background-color: var(--bg, #f7f7f4);
}

/* 右侧面板：SQL编辑器 */
.editor-sidebar {
  background-color: var(--card-bg, #ffffff);
  border-left: 1px solid var(--border, #e6e6e2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  transition: width 0s ease;
  padding: 24px;
}

/* 拖拽分界线 */
.resize-handle {
  position: absolute;
  width: 6px;
  height: 100%;
  background-color: transparent;
  cursor: ew-resize;
  z-index: 100;
  transition: background-color 0.2s;
}

.resize-handle:hover {
  background-color: var(--primary, #4a7c59);
  opacity: 0.5;
}

.resize-handle.left-resize {
  top: 0;
  bottom: 0;
}

.resize-handle.right-resize {
  top: 0;
  bottom: 0;
}

/* 确保拖拽时鼠标样式正确 */
.sql-main.resizing {
  cursor: ew-resize;
}

/* 调整编辑器样式 */
.editor-sidebar .toolbar {
  margin-bottom: 16px;
}

.editor-sidebar .sql-editor {
  flex: 1;
  height: auto;
  min-height: 300px;
}

/* 历史操作面板样式 */
.history-panel {
  margin-top: 12px;
  border: 1px solid var(--border, #e6e6e2);
  border-radius: 8px;
  background-color: var(--card-bg, #ffffff);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.history-header {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border, #e6e6e2);
  background-color: var(--bg, #f7f7f4);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.history-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text, #2d3436);
}

.history-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.history-actions .btn {
  padding: 4px 10px;
  font-size: 0.8rem;
}

.history-actions .close-btn {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border, #e6e6e2);
  font-size: 1.2rem;
  cursor: pointer;
  color: var(--text, #2d3436);
  padding: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.history-actions .close-btn:hover {
  background-color: var(--primary, #4a7c59);
  color: white;
  border-color: var(--primary, #4a7c59);
}

.history-list {
  padding: 4px;
}

.empty-history {
  text-align: center;
  padding: 24px;
  color: var(--text-secondary, #636e72);
  font-size: 0.9rem;
}

.history-item {
  padding: 8px;
  border-radius: 6px;
  margin-bottom: 4px;
  background-color: var(--bg, #f7f7f4);
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.history-item:hover {
  background-color: var(--primary, #4a7c59);
  color: white;
  transform: translateX(4px);
}

.history-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 0.8rem;
  color: var(--text-secondary, #636e72);
}

.history-item:hover .history-info {
  color: rgba(255, 255, 255, 0.9);
}

.history-timestamp {
  font-weight: 500;
}

.history-user {
  background-color: rgba(96, 153, 102, 0.2);
  color: var(--success, #609966);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.history-item:hover .history-user {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.history-sql {
  font-family: 'Fira Code', monospace;
  font-size: 0.8rem;
  line-height: 1.4;
  word-break: break-all;
  white-space: pre-wrap;
  color: var(--text, #2d3436);
  margin-bottom: 4px;
  text-align: left;
}

.history-item:hover .history-sql {
  color: white;
}

.history-action {
  display: flex;
  justify-content: flex-end;
}

.select-btn {
  background-color: rgba(96, 153, 102, 0.2);
  color: var(--success, #609966);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.2s;
}

.history-item:hover .select-btn {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  opacity: 1;
}

/* 调整结果区域样式 */
.middle-section .result-section {
  max-width: 100%;
}

.database-sidebar {
  background-color: var(--card-bg, #ffffff);
  border-right: 1px solid var(--border, #e6e6e2);
  display: flex;
  flex-direction: column;
  overflow: visible;
  position: relative;
  transition: width 0.3s ease;
}

.database-sidebar.compact .sidebar-header h3 {
  display: none;
}

.database-sidebar.compact .table-name {
  display: none;
}

.database-sidebar.compact .table-item {
  justify-content: center;
  padding: 10px 0;
}

.compact-toggle-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: var(--text-secondary, #636e72);
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.compact-toggle-btn:hover {
  background-color: var(--bg, #f0f0f0);
  color: var(--text, #2d3436);
}



.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border, #e6e6e2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: padding 0.3s ease;
}

.database-sidebar.compact .sidebar-header {
  padding: 16px 8px;
  justify-content: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text, #2d3436);
}

.table-list {
  flex: 1;
  padding: 12px;
  position: relative;
  /* 添加内部容器处理滚动 */
  display: flex;
  flex-direction: column;
}

.table-list-scrollable {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
}

.table-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
  position: relative;
}

.table-item:hover {
  background-color: var(--bg, #f0f0f0);
  transform: translateX(4px);
}

.table-icon {
  font-size: 1.1rem;
}

.table-name {
  font-weight: 500;
  color: var(--text, #2d3436);
}

.table-tooltip {
  position: fixed;
  background-color: #2d3436;
  border-radius: 8px;
  padding: 12px;
  min-width: 280px;
  max-width: 400px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  z-index: 9999;
  opacity: 1;
  visibility: visible;
  transition: all 0.3s ease;
  pointer-events: none; /* 确保tooltip不影响鼠标事件 */
  transform: translateX(8px);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-8px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.tooltip-header {
  font-size: 0.85rem;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.tooltip-body {
  max-height: 300px;
  overflow-y: auto;
}

.column-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 0.8rem;
  color: #ccc;
}

.col-name {
  flex: 1;
  font-weight: 500;
  color: #fff;
}

.col-type {
  background-color: rgba(96, 153, 102, 0.3);
  color: #609966;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.col-pk {
  font-size: 0.9rem;
}

.no-columns {
  color: #888;
  font-size: 0.8rem;
  text-align: center;
  padding: 12px 0;
}

.empty-state {
  text-align: center;
  color: var(--text-secondary, #888);
  padding: 40px 20px;
  font-size: 0.9rem;
  background-color: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 12px;
  min-height: 200px;
}

.empty-state::before {
  content: "📁";
  font-size: 3rem;
  opacity: 0.3;
}

/* 左侧面板中的空状态样式 */
.database-sidebar .empty-state {
  padding: 60px 20px;
  min-height: 250px;
}

.editor-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px;
  gap: 16px;
  overflow-y: auto;
}

.toolbar {
  display: flex;
  gap: 12px;
}

.sql-editor {
  width: 100%;
  height: 200px;
  padding: 16px;
  border: 1px solid var(--border, #ccc);
  border-radius: 8px;
  background-color: var(--input-bg, #fafaf9);
  color: var(--text, #333);
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  box-sizing: border-box;
}

.sql-editor:focus {
  outline: none;
  border-color: var(--primary, #4a7c59);
}

.result-section {
  flex: 1;
  overflow-y: auto;
}

.message {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}
.message.error { background-color: rgba(207, 92, 92, 0.1); color: var(--danger, #cf5c5c); }
.message.success { background-color: rgba(96, 153, 102, 0.1); color: var(--success, #609966); }

.result-table-wrapper {
  overflow-x: auto;
  border: 1px solid var(--border, #eee);
  border-radius: 8px;
  background: var(--card-bg, #fff);
  margin-bottom: 24px;
}

.result-table {
  width: 100%;
  border-collapse: collapse;
}

.result-table th, .result-table td {
  padding: 10px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border, #eee);
}

.result-table th {
  background-color: var(--bg, #f9f9f9);
  font-weight: 600;
}

.result-meta {
  padding: 8px 16px;
  font-size: 0.8em;
  color: var(--text-secondary, #888);
  text-align: right;
  background: var(--bg, #f9f9f9);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background-color: var(--card-bg, #ffffff);
  border-radius: 12px;
  max-width: 800px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  animation: slideUp 0.3s ease-out;
}

.modal-content.small {
  max-width: 400px;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border, #e6e6e2);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary, #888);
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.modal-close:hover {
  background-color: var(--bg, #f0f0f0);
  color: var(--text, #2d3436);
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  max-height: calc(80vh - 60px);
}

.structure-section {
  margin-bottom: 24px;
}

.structure-section h4 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text, #2d3436);
}

.structure-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
}

.structure-table th, .structure-table td {
  padding: 10px 12px;
  text-align: left;
  border: 1px solid var(--border, #e6e6e2);
}

.structure-table th {
  background-color: var(--bg, #f9f9f9);
  font-weight: 600;
  font-size: 0.9rem;
}

.structure-table td {
  font-size: 0.9rem;
}

.pk-badge {
  display: inline-block;
  padding: 2px 8px;
  background-color: var(--primary, #4a7c59);
  color: white;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.input-field {
  width: 100%;
  padding: 10px 12px;
  background-color: var(--input-bg, #fafaf9);
  color: var(--text, #2d3436);
  border: 1px solid var(--border, #ccc);
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
  margin-bottom: 16px;
  transition: border-color 0.2s;
}

.input-field:focus {
  outline: none;
  border-color: var(--primary, #4a7c59);
  box-shadow: 0 0 0 2px rgba(74, 124, 89, 0.2);
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
  background-color: var(--primary, #4a7c59);
  color: white;
}
.btn:hover { opacity: 0.9; transform: translateY(-1px); }
.btn:active { transform: translateY(0); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn.primary { background-color: var(--primary, #4a7c59); color: white; }
.btn.secondary { background-color: var(--text-secondary, #636e72); color: white; }
.btn.sm { font-size: 0.85rem; padding: 6px 12px; }

[data-theme="dark"] .sql-editor {
  background-color: #2d2d2d;
  color: #e0e0e0;
  border-color: #404040;
}


</style>
