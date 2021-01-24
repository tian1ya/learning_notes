### Java 函数优雅之道上

---

**导读**： 随着软件项目代码的日积月累，系统维护成本越来越高，需要持续的优化代码，提高代码质量，软件系统思维有句话 "Think more, code less" 需要多思考，编码越少，在编程中多思考总结，努力提升自己的编码水平才能写出更好，更优质的代码。

---

**编码规则**

**使用通用工具函数**

**1. **

> 现象描述：
>
> ```java
> thisName != null && thisName.equals(name)
> ```
>
> 更加完善的写法：
>
> ```java
> (thisName == name) || (thisName != null && thisName.equals(name))
> ```
>
> 建议方法：
>
> ```java
> Objects.equals(name, thisName);
> ```
>
> 在 Objects.equals 的实现就是使用，上面更加完善的写法，如果使用这个工具，可读性更高

**2**

> 现象描述
>
> ```java
> ! (list == null || list.isEmpty()) 
> ```
>
> 建议方案
>
> ```java
> import org.apache.commons.collections4.CollectionUtils;
> CollectionUtils.isNotEmpty(list);
> ```
>
> CollectionUtils.isNotEmpty(list) 的实现就是上面的现象描述，
>
> CollectionUtils 中还比较多的工具。

使用上面的工具，首先带来的好处就是业务代码减少，逻辑一目了然，而且使用通用的工具，逻辑考虑周全，出问题的概率也低

**产分超大逻辑**

当一个函数超过80行之后，就属于超大函数，需要进行拆分

**1**

> 每一个代码快，都可以封装为一个函数，这里建议每一个函数代码块都添加一个注释，用于解释代码块的功能，如果不给注释，那么这里函数的命名就显得非常的重要。根据函数的名称就明白这个函数所要完成的功能。
>
> ```
> // 每日生活函数public void liveDaily() {    
> 		// 吃饭    
> 		// 吃饭相关代码几十行
>     // 编码    
>     // 编码相关代码几十行
>     // 睡觉    
>     // 睡觉相关代码几十行
> }
> ```
>
> 建议方案
>
> ```java
> // 每日生活函数public void liveDaily() {    
> 		// 吃饭
>     eat();    
> 		// 编码
>     code();    
> 		// 睡觉
>     sleep();
> }	
> // 吃饭函数private void eat() {    
> 		// 吃饭相关代码
> }
>   
> // 编码函数private void code() {    
> 		// 编码相关代码
> }
> // 睡觉函数private void sleep() {
> 		// 睡觉相关代码
> }
> ```
>
> 每一个循环体都可以看做是一个代码块，封装抽出到一个函数
>
> ```java
> // 生活函数public void live() {    
> 	while (isAlive) {        
>     		// 吃饭
>         eat();        
>     		// 编码
>         code();        
>     		// 睡觉
>         sleep();
>     }
> }
> ```
>
> 建议方案
>
> ```java
> // 生活函数
> public void live() {    
> 	while (isAlive) {        
>     		// 每日生活
>         liveDaily();
>     }
> 
> }
> // 每日生活函数
> private void liveDaily() {    
>   	// 吃饭
>     eat();    
>   	// 编码
>     code();    
>   	// 睡觉
>     sleep();
> }
> ```
>
> 每一个条件都可以封装为一个函数
>
> ```java
> // 外出函数
> public void goOut() {    
>   	// 判断是否周末
>     // 判断是否周末: 是周末则游玩
>     if (isWeekday()) {        
>       	// 游玩代码几十行
>     }    // 判断是否周末: 非周末则工作
>     else {        
>       // 工作代码几十行
>     }
> }
> ```
>
> 建议方案
>
> ```java
> // 外出函数public void goOut() {    
> // 判断是否周末
> // 判断是否周末: 是周末则游玩
>     if (isWeekday()) {
>         play();
>     }    // 判断是否周末: 非周末则工作
>     else {
>         work();
>     }
> }
> // 游玩函数
> private void play() {    
>   // 游玩代码几十行
> }
> // 工作函数
> private void work() {    
>   // 工作代码几十行
> }
> ```
>
> 以上的函数块抽离，主要带来的好处就是，
>
> * 函数功能短小精悍，功能就越单一，往往声明周期就较长
> * 一个函数越长，越容易理解和维护，维护人员就不敢轻易修改
> * 在过长函数中，往往会发现难以发现的重复代码

**同一函数内代码块级别尽量一致**

> 现象描述
>
> ```java
> // 每日生活函数
> public void liveDaily() {    
>   	// 吃饭
>     eat();    
>   	// 编码
>     code();    
>   	// 睡觉
>     // 睡觉相关代码几十行
> }
> ```
>
> 很明显，睡觉这块代码块，跟eat（吃饭）和code（编码）不在同一级别上，显得比较突兀。如果把写代码比作写文章，eat（吃饭）和code（编码）是段落大意，而睡觉这块代码块属于一个详细段落。而在liveDaily（每日生活）这个函数上，只需要写出主要流程（段落大意）即可。
>
> 建议方案
>
> ```java
> public void liveDaily() {    // 吃饭
>     eat();    // 编码
>     code();    // 睡觉
>     sleep();
> }
> // 睡觉
> private void sleep() {    
>   // 睡觉相关代码
> }
> ```
>
> 主要收益
>
> * 函数调用表明用途，函数实现表达逻辑，层次分明便于理解；
> * 不用层次的代码块放在一个函数中，容易让人觉得代码头重脚轻。

**封装相同功能代码为函数**

**封装相同代码为函数**

> 现象描述：
>
> ```java
> // 禁用用户函数
> public void disableUser() {    
>   // 禁用黑名单用户    
>   List<Long> userIdList = queryBlackUser();    
>   for (Long userId : userIdList) {        
>     User userUpdate = new User();        
>     userUpdate.setId(userId);        
>     userUpdate.setEnable(Boolean.FALSE);        
>     userDAO.update(userUpdate);    
>   }    
>   // 禁用过期用户    
>   userIdList = queryExpiredUser();    
>   for (Long userId : userIdList) {        
>     User userUpdate = new User();        
>     userUpdate.setId(userId);        
>     userUpdate.setEnable(Boolean.FALSE);        
>     userDAO.update(userUpdate);    
>   }
> }
> ```
>
> 建议方案：
>
> ```java
> // 禁用用户函数
> public void disableUser() {    
>   // 禁用黑名单用户    
>   List<Long> userIdList = queryBlackUser();    
>   for (Long userId : userIdList) {
>     disableUser(userId);    
>   }    
>   // 禁用过期用户    
>   userIdList = queryExpiredUser();    
>   for (Long userId : userIdList) {        
>     disableUser(userId);    
>   }}
> // 禁用用户函数
> private void disableUser(Long userId) {    
>   User userUpdate = new User();    
>  	userUpdate.setId(userId);    
>   userUpdate.setEnable(Boolean.FALSE);    
>   userDAO.update(userUpdate);
> }
> ```
>
> 封装相似代码为函数
>
> 封装相似代码为函数，差异性通过函数参数控制。
>
> 现象描述：
>
> ```java
> // 通过工单函数
> public void adoptOrder(Long orderId) {
>     Order orderUpdate = new Order();
>     orderUpdate.setId(orderId);
>     orderUpdate.setStatus(OrderStatus.ADOPTED);
>     orderUpdate.setAuditTime(new Date());
>     orderDAO.update(orderUpdate);
> }
> // 驳回工单函数
> public void rejectOrder(Long orderId) {
>     Order orderUpdate = new Order();
>     orderUpdate.setId(orderId);
>     orderUpdate.setStatus(OrderStatus.REJECTED);
>     orderUpdate.setAuditTime(new Date());
>     orderDAO.update(orderUpdate);
> }
> ```
>
> 建议方案：
>
> ```java
> // 通过工单函数
> public void adoptOrder(Long orderId) {
>     auditOrder(orderId, OrderStatus.ADOPTED);
> }
> // 驳回工单函数
> public void rejectOrder(Long orderId) {
>     auditOrder(orderId, OrderStatus.REJECTED);
> }
> // 审核工单函数
> private void auditOrder(Long orderId, OrderStatus orderStatus) {
>     Order orderUpdate = new Order();
>     orderUpdate.setId(orderId);
>     orderUpdate.setStatus(orderStatus);
>     orderUpdate.setAuditTime(new Date());
>     orderDAO.update(orderUpdate);
> }
> ```
>
> 主要收益
>
> * 封装公共函数，减少代码行数，提高代码质量；
> * 封装公共函数，使业务代码更精炼，可读性可维护性更强。

**封装获取参数值函数**

> 现象描述：
>
> ```java
> // 是否通过函数
> public boolean isPassed(Long userId) {    
>   // 获取通过阈值    
>   double thisPassThreshold = PASS_THRESHOLD;    
>   if (Objects.nonNull(passThreshold)) {        
>     thisPassThreshold = passThreshold;    
>   }    
>   // 获取通过率    
>   double passRate = getPassRate(userId);    
>   // 判读是否通过    
>   return passRate >= thisPassThreshold;
> }
> ```
>
> 建议方案
>
> ```java
> // 是否通过函数
> public boolean isPassed(Long userId) {    
>   // 获取通过阈值    
>   double thisPassThreshold = getPassThreshold();    
>   // 获取通过率    
>   double passRate = getPassRate(userId);    
>   // 判读是否通过    
>   return passRate >= thisPassThreshold;}
> 
> 	// 获取通过阈值函数
>   private double getPassThreshold() {    
>     if (Objects.nonNull(passThreshold)) {        
>       return passThreshold;    
>     }    
>     return PASS_THRESHOLD;
> }
> ```

**通过接口参数化封装相同逻辑**

> 现象描述：
>
> ```java
> // 发送审核员结算数据函数
> public void sendAuditorSettleData() {
>     List<WorkerSettleData> settleDataList = auditTaskDAO.statAuditorSettleData();    
>   	for (WorkerSettleData settleData : settleDataList) {
>         WorkerPushData pushData = new WorkerPushData();
>         pushData.setId(settleData.getWorkerId());
>         pushData.setType(WorkerPushDataType.AUDITOR);
>         pushData.setData(settleData);
>         pushService.push(pushData);
>     }
> }
> // 发送验收员结算数据函数
> public void sendCheckerSettleData() {
>     List<WorkerSettleData> settleDataList = auditTaskDAO.statCheckerSettleData();    
>   	for (WorkerSettleData settleData : settleDataList) {
>         WorkerPushData pushData = new WorkerPushData();
>         pushData.setId(settleData.getWorkerId());
>         pushData.setType(WorkerPushDataType.CHECKER);
>         pushData.setData(settleData);
>         pushService.push(pushData);
>     }
> ```
>
> 建议方案
>
> ```java
> // 发送审核员结算数据函数
> public void sendAuditorSettleData() {
>     sendWorkerSettleData(WorkerPushDataType.AUDITOR, () -> 		
>                          				auditTaskDAO.statAuditorSettleData());
> }
> // 发送验收员结算数据函数
> public void sendCheckerSettleData() {
>     sendWorkerSettleData(WorkerPushDataType.CHECKER, () -> 
>                          auditTaskDAO.statCheckerSettleData());
> }
> // 发送作业员结算数据函数
> public void sendWorkerSettleData(WorkerPushDataType dataType, WorkerSettleDataProvider dataProvider) {
>     List<WorkerSettleData> settleDataList = dataProvider.statWorkerSettleData();    
>   	for (WorkerSettleData settleData : settleDataList) {
>         WorkerPushData pushData = new WorkerPushData();
>         pushData.setId(settleData.getWorkerId());
>         pushData.setType(dataType);
>         pushData.setData(settleData);
>         pushService.push(pushData);
>     }
> }
> // 作业员结算数据提供者接口
> private interface WorkerSettleDataProvider {    
>   	// 统计作业员结算数据
>     public List<WorkerSettleData> statWorkerSettleData();
> }
> ```
>
> **主要收益**
>
> - 把核心逻辑从各个业务函数中抽析，使业务代码更清晰更易维护；
> - 避免重复性代码多次编写，精简重复函数越多收益越大。

**减少函数代码层级**

> 如果要使函数优美，建议函数代码层级在1-4之间，过多的缩进会让函数难以阅读。
>
> 利用return提前返回函数
>
> ```java
> // 获取用户余额函数
> public Double getUserBalance(Long userId) {
>     User user = getUser(userId);    
> 		if (Objects.nonNull(user)) {
>         UserAccount account = user.getAccount();        
>     if (Objects.nonNull(account)) {            
>       	return account.getBalance();
>       }
>     }    
> 	return null;
> }
> ```
>
> 建议方案
>
> ```java
> // 获取用户余额函数
> public Double getUserBalance(Long userId) {    
>   // 获取用户信息    
>   User user = getUser(userId);    
>   if (Objects.isNull(user)) {        
>     return null;    
>   }    
>   // 获取用户账户    
>   UserAccount account = user.getAccount();    
>   if (Objects.isNull(account)) {        
>     return null;    
>   }    
>   // 返回账户余额    
>   return account.getBalance();
> }
> ```
>
> 利用continue提前结束循环
>
> ```java
> // 获取合计余额函数
> public double getTotalBalance(List<User> userList) {    
>   // 初始合计余额    
>   double totalBalance = 0.0D;    
>   // 依次累加余额    
>   for (User user : userList) {        
>     // 获取用户账户        
>     UserAccount account = user.getAccount();        
>     if (Objects.nonNull(account)) {            
>       // 累加用户余额            
>       Double balance = account.getBalance();            
>       if (Objects.nonNull(balance)) {                
>         totalBalance += balance;            
>       }        
>     }    
>   }    
>   // 返回合计余额    
>   return totalBalance;
> }
> ```
>
> 建议方案
>
> ```java
> // 获取合计余额函数
> public double getTotalBalance(List<User> userList) {    
>   // 初始合计余额    
>   double totalBalance = 0.0D;    
>   // 依次累加余额    
>   for (User user : userList) {        
>     // 获取用户账户        
>     UserAccount account = user.getAccount();        
>     if (Objects.isNull(account)) {            
>       continue;        
>     }        
>     // 累加用户余额        
>     Double balance = account.getBalance();        
>     if (Objects.nonNull(balance)) {            
>       totalBalance += balance;        
>     }    
>   }    
>   // 返回合计余额    
>   return totalBalance;
> }
> ```

**特殊说明**

> 其它方式：在循环体中，先调用案例1的函数getUserBalance(获取用户余额)，再进行对余额进行累加。
>
> 在循环体中，建议最多使用一次continue。如果需要有使用多次continue的需求，建议把循环体封装为一个函数。

**案例三：利用条件表达式函数减少层级**

> 请参考下一章的"案例2: 把复杂条件表达式封装为函数"
>
> - 代码层级减少，代码缩进减少；
> - 模块划分清晰，方便阅读维护。

**封装条件表达式函数**

> **案例一：把简单条件表达式封装为函数**
>
> 现象描述：
>
> ```java
> // 获取门票价格函数
> public double getTicketPrice(Date currDate) {    
>   if (Objects.nonNull(currDate) && currDate.after(DISCOUNT_BEGIN_DATE) && 			
>       																	currDate.before(DISCOUNT_END_DATE)) {        
>     			return TICKET_PRICE * DISCOUNT_RATE;    
>   }    
>   return TICKET_PRICE;
> }
> ```
>
> 建议方案：
>
> ```java
> // 获取门票价格函数
> public double getTicketPrice(Date currDate) {    
>   if (isDiscountDate(currDate)) {        
>     return TICKET_PRICE * DISCOUNT_RATE;    
>   }    
>   return TICKET_PRICE;
> }
> // 是否折扣日期函数
> private static boolean isDiscountDate(Date currDate) {    
>   return Objects.nonNull(currDate) && currDate.after(DISCOUNT_BEGIN_DATE) && 	
>     																						currDate.before(DISCOUNT_END_DATE);}
> ```
>
> 把复杂条件表达式封装为函数
>
> 现象描述
>
> ```java
> // 获取土豪用户列表
> public List<User> getRichUserList(List<User> userList) {    
>   // 初始土豪用户列表    
>   List<User> richUserList = new ArrayList<>();    
>   // 依次查找土豪用户    
>   for (User user : userList) {        
>     // 获取用户账户        
>     UserAccount account = user.getAccount();        
>     if (Objects.nonNull(account)) {            
>       // 判断用户余额            
>       Double balance = account.getBalance();            
>       if (Objects.nonNull(balance) && balance.compareTo(RICH_THRESHOLD) >= 0) {                
>         	// 添加土豪用户                
>         richUserList.add(user);            
>       }        
>     }    
>   }    
>   // 返回土豪用户列表    
>   return richUserList;
> }
> ```
>
> 建议方案：
>
> ```java
> // 获取土豪用户列表
> public List<User> getRichUserList(List<User> userList) {    
>   	// 初始土豪用户列表
>     List<User> richUserList = new ArrayList<>();    
>   	// 依次查找土豪用户,这里可以考虑使用Stream 实现
>     for (User user : userList) {        
>       // 判断土豪用户,
>         if (isRichUser(user)) {            
>           // 添加土豪用户
>             richUserList.add(user);
>         }
>     }    
>   	// 返回土豪用户列表
>     return richUserList;
> }
> // 是否土豪用户
> private boolean isRichUser(User user) {    
>   // 获取用户账户
>     UserAccount account = user.getAccount();    
>   	if (Objects.isNull(account)) {        
>       	return false;
>     }    
>   	// 获取用户余额
>     Double balance = account.getBalance();    
>   	if (Objects.isNull(balance)) {        
>       	return false;
>     }    
>   	// 比较用户余额
>     return balance.compareTo(RICH_THRESHOLD) >= 0;
> }
> ```

**尽量避免不必要的空指针判断**

> 本章只适用于项目内部代码，并且是自己了解的代码，才能够尽量避免不必要的空指针判断。**对于第三方中间件和系统接口，必须做好空指针判断，以保证代码的健壮性。**
>
> 调用函数保证参数不为空，被调用函数尽量避免不必要的空指针判断
>
> 现象描述
>
> ```java
> // 创建用户信息
> User user = new User();
> 	... 
>     // 赋值用户相关信息
>     createUser(user);
>     // 创建用户函数
> 		private void createUser(User user){    
>       // 判断用户为空    
>       if(Objects.isNull(user)) {        
>         return;    
>       }    
>       // 创建用户信息    
>       userDAO.insert(user);    
>       userRedis.save(user);
>     }
> ```
>
> 建议方案
>
> ```java
> // 创建用户信息
> User user = new User();
> 	... 
>   // 赋值用户相关信息
>   createUser(user);
> 	// 创建用户函数
> 	private void createUser(User user){    
>     // 创建用户信息    
>     userDAO.insert(user);    
>     userRedis.save(user);
>   }
> ```
>
> 被调用函数保证返回不为空,调用函数尽量避免不必要的空指针判断
>
> 现象描述
>
> ```java
> // 保存用户函数
> public void saveUser(Long id, String name) {    
>   // 构建用户信息    
>   User user = buildUser(id, name);    
>   if (Objects.isNull(user)) {        
>     throw new BizRuntimeException("构建用户信息为空");    
>   }    
>   // 保存用户信息    
>   userDAO.insert(user);    
>   userRedis.save(user);}
> 	// 构建用户函数
> 	private User buildUser(Long id, String name) {    
>     User user = new User();    
>     user.setId(id);    
>     user.setName(name);    
>     return user;
>   }
> ```
>
> 建议方案
>
> ```java
> // 保存用户函数
> public void saveUser(Long id, String name) {    
>   // 构建用户信息    
>   User user = buildUser(id, name);    
>   // 保存用户信息    
>   userDAO.insert(user);    
>   userRedis.save(user);}
> 	// 构建用户函数
> 	private User buildUser(Long id, String name) {    
>     	User user = new User();    
>     	user.setId(id);    
>     	user.setName(name);    
>     	return user;
>   }
> ```

**内部函数参数尽量使用基础类型**

> * 内部函数尽量使用基础类型，避免了隐式封装类型的打包和拆包；
> * 内部函数参数使用基础类型，用语法上避免了内部函数的参数空指针判断；
> * 内部函数返回值使用基础类型，用语法上避免了调用函数的返回值空指针判断。

**尽量避免返回的数组和列表为null**

**尽量避免返回的列表为null，引起不必要的空指针判断**

**当传入参数过多时，应封装为参数类**

> Java规范不允许函数参数太多，不便于维护也不便于扩展。
>
> ```Java
> public void modifyUser(Long id, String name, String phone, Integer age, Integer sex){}
> 
> private class User{
>   private Long id;
>   private String name;
>   private String phone;
>   private Integer age;
>   private Integer sex;
> }
> 
> public void modifyUser(User user)
> ```

**尽量用函数替换匿名内部类的实现**

- 首先推荐用Lambda表达式简化匿名内部类，其次推荐用函数替换复杂的Lambda表达式的实现。











